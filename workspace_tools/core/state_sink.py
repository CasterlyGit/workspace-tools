"""StateSink — writes live pipeline progress into the per-repo inbox state
file so the user's `_status.md` table can show stage X/N as the agent
advances. Loose coupling: writes JSON, doesn't talk to the watcher directly.

Schema appended into <repo>/inbox/.state.json under the matching ticket entry:

    "current_stage": "design"           # or null when idle
    "stage_index":   3                   # 1-based
    "total_stages":  7
    "stage_history": [
      {"name":"explore",  "ok":true,  "ended_at":"2026-..."},
      {"name":"research", "ok":true,  "ended_at":"2026-..."},
      ...
    ]
    "shape":         "full"
    "last_activity": "writing src/foo.py …"  # rolling sub-stage breadcrumb
    "last_updated":  "2026-..."

The `regenerate_status` function in inbox-process.sh is responsible for
rendering these fields. This module never touches markdown."""
from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path


class StateSink:
    def __init__(self, *, repo_path: Path, issue_number: int, total_stages: int):
        self.repo_path = repo_path
        self.issue_number = issue_number
        self.total_stages = total_stages
        self._state_file = repo_path / "inbox" / ".state.json"
        self._index = 0
        self._last_activity_write = 0.0  # monotonic seconds, for throttling

    # ── public API matched to PipelineHooks ──────────────────────────────────

    def start(self, shape: str, total_stages: int) -> None:
        self.total_stages = total_stages
        self._mutate(lambda e: {
            **e,
            "shape": shape,
            "total_stages": total_stages,
            "current_stage": None,
            "stage_index": 0,
            "stage_history": e.get("stage_history") or [],
            "agent_done": False,
            "iterated": True,
            "last_updated": _now(),
        })

    def stage_start(self, name: str) -> None:
        self._index += 1
        self._last_activity_write = 0.0  # let the first line of this stage publish immediately
        self._mutate(lambda e: {
            **e,
            "current_stage": name,
            "stage_index": self._index,
            "last_activity": None,
            "last_updated": _now(),
        })

    def note_activity(self, line: str) -> None:
        """Sub-stage breadcrumb. Called once per agent stdout line; throttled
        so we don't rewrite the JSON on every token."""
        line = (line or "").strip()
        if not line:
            return
        now = time.monotonic()
        if now - self._last_activity_write < 2.0:
            return
        self._last_activity_write = now
        snippet = line[:120]
        self._mutate(lambda e: {
            **e,
            "last_activity": snippet,
            "last_updated": _now(),
        })

    def stage_done(self, name: str, ok: bool) -> None:
        self._mutate(lambda e: {
            **e,
            "stage_history": (e.get("stage_history") or []) + [
                {"name": name, "ok": ok, "ended_at": _now()}
            ],
            "last_updated": _now(),
        })

    def finish(self, *, all_ok: bool) -> None:
        self._mutate(lambda e: {
            **e,
            "current_stage": None,
            "last_activity": None,
            "agent_done": True,
            "ok": all_ok,
            "last_updated": _now(),
        })

    # ── internals ─────────────────────────────────────────────────────────────

    def _mutate(self, fn) -> None:
        """Atomic read-modify-write of the JSON file. The state.json is shared
        with inbox-process.sh, so we must not partially-write it."""
        try:
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                blob = json.loads(self._state_file.read_text() or "{}")
            except (FileNotFoundError, json.JSONDecodeError):
                blob = {}

            # Find the entry matching this issue number (by `url` ending in /issues/N)
            target_key = None
            for key, entry in blob.items():
                if not isinstance(entry, dict):
                    continue
                url = entry.get("url") or ""
                if url.rstrip("/").endswith(f"/issues/{self.issue_number}"):
                    target_key = key
                    break
            if target_key is None:
                # Unknown ticket — write under a synthetic key so progress isn't lost
                target_key = f"issue-{self.issue_number}.virtual"
                blob.setdefault(target_key, {
                    "status": "filed",
                    "url": f"https://github.com/.../issues/{self.issue_number}",
                    "title": f"issue #{self.issue_number}",
                    "pr_num": None,
                })

            existing = blob.get(target_key) or {}
            blob[target_key] = fn(existing)

            # Atomic write
            tmp = tempfile.NamedTemporaryFile("w", delete=False,
                                              dir=str(self._state_file.parent),
                                              prefix=".state.", suffix=".tmp")
            json.dump(blob, tmp, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp.close()
            os.replace(tmp.name, self._state_file)
        except Exception as e:
            # State sink must never crash the pipeline
            print(f"[state-sink] write failed: {e}", flush=True)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")
