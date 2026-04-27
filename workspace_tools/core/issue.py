"""Read-side helpers for GitHub issues. Kept narrow — anything more elaborate
moves into a separate module."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .git_ops import run


@dataclass
class Issue:
    repo_full: str
    number: int
    title: str
    body: str
    url: str
    comments: list[dict]
    labels: list[str]

    @property
    def repo_owner(self) -> str: return self.repo_full.split("/", 1)[0]
    @property
    def repo_name(self) -> str: return self.repo_full.split("/", 1)[1]

    def aggregated_text(self) -> str:
        """Title + body + every comment body — what the model needs to read."""
        parts = [f"# {self.title}", "", self.body or "_(no body)_"]
        for c in self.comments:
            parts.append("")
            parts.append("---")
            parts.append(f"_Comment by {c.get('author', {}).get('login', '?')}:_")
            parts.append(c.get("body", ""))
        return "\n".join(parts)

    def user_feedback(self) -> str | None:
        """Extract the last comment (assumed to be user feedback on the PR).
        Returns the comment body, or None if there are no comments."""
        if not self.comments:
            return None
        return self.comments[-1].get("body", "")


_URL_RE = re.compile(r"https?://github\.com/([^/]+/[^/]+)/(issues|pull)/(\d+)")


def parse_issue_ref(ref: str) -> tuple[str, int]:
    """Accepts a full issue/PR URL, or `owner/repo#N`, or `#N` (must be in repo dir)."""
    m = _URL_RE.search(ref)
    if m:
        return m.group(1), int(m.group(3))  # group 3 is the number (after repo and type)
    if "#" in ref:
        repo, num = ref.split("#", 1)
        return repo.strip(), int(num)
    raise ValueError(f"can't parse issue reference: {ref!r}")


def fetch_issue(repo_full: str, number: int) -> Issue:
    out = run([
        "gh", "issue", "view", str(number),
        "--repo", repo_full,
        "--json", "title,body,url,comments,labels"
    ])
    data = json.loads(out)
    return Issue(
        repo_full=repo_full,
        number=number,
        title=data["title"],
        body=data.get("body") or "",
        url=data["url"],
        comments=data.get("comments") or [],
        labels=[l["name"] for l in data.get("labels") or []],
    )
