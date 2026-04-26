"""Agent — wraps the actual LLM invocation.

Today: subprocesses `claude --print --dangerously-skip-permissions`.
Tomorrow: this is the only place that needs to change to swap providers,
add cost tracking, retries, streaming, multiple-model fallback, etc.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


_CLAUDE = os.environ.get("CLAUDE_CLI") or shutil.which("claude") or "claude"


@dataclass
class AgentResult:
    returncode: int
    stdout: str
    stderr: str
    duration_s: float

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass
class AgentInvocation:
    """A single agent call. Constructed by stages, executed by Agent."""
    prompt: str
    cwd: Path
    timeout_s: int = 600
    extra_args: list[str] = field(default_factory=list)

    # Hooks — extension points filled in by Pipeline / observers
    label: str = ""
    on_line: callable | None = None     # called with each stdout line as it arrives


class Agent:
    """Default agent backend: claude CLI in print mode."""

    def __init__(self, binary: str = _CLAUDE):
        self.binary = binary

    def run(self, inv: AgentInvocation) -> AgentResult:
        import time
        cmd = [self.binary, "--print", "--dangerously-skip-permissions", *inv.extra_args, inv.prompt]

        t0 = time.time()
        try:
            proc = subprocess.Popen(
                cmd, cwd=str(inv.cwd),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace",
                bufsize=1,
                start_new_session=True,
            )
        except FileNotFoundError as e:
            return AgentResult(returncode=127, stdout="", stderr=str(e), duration_s=0.0)

        out_chunks: list[str] = []
        try:
            assert proc.stdout is not None
            for raw in proc.stdout:
                out_chunks.append(raw)
                if inv.on_line:
                    try: inv.on_line(raw.rstrip("\n"))
                    except Exception: pass
            try:
                proc.wait(timeout=inv.timeout_s)
            except subprocess.TimeoutExpired:
                proc.kill()
                return AgentResult(returncode=124, stdout="".join(out_chunks),
                                   stderr=f"timeout after {inv.timeout_s}s",
                                   duration_s=time.time() - t0)
        except KeyboardInterrupt:
            proc.terminate()
            raise

        err = proc.stderr.read() if proc.stderr else ""
        return AgentResult(returncode=proc.returncode or 0,
                           stdout="".join(out_chunks),
                           stderr=err,
                           duration_s=time.time() - t0)
