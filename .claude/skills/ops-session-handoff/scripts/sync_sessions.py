#!/usr/bin/env python3
"""Archive the host's raw chat-session transcripts into a durable workspace store.

Part of the ops-session-handoff skill (transcript-archive capability). Contract:
copy any new-or-grown session transcript from the host AI harness's own session
store into a durable folder inside the workspace, idempotently. Rationale: session
indexes often carry session rows without turn content, and host stores live outside
the workspace keyed to volatile identifiers — a chat-approved decision that was
never persisted to disk is otherwise unrecoverable (lesson L-22).

Run at session end (handoff workflow) AND at the next session start (catch-up):
transcripts are appended live, so an end-of-session copy misses its own final
turns; the next run re-copies any file that grew. Running twice is harmless.

Host adapters: transcript discovery is host-specific. Each adapter returns the
transcript files belonging to this workspace. Adding a host = adding one discovery
function and registering it in HOST_ADAPTERS. Currently implemented:

- claude-code: Claude Code CLI sessions —
  <CLAUDE_CONFIG_DIR|~/.claude>/projects/<slugified-workspace>/<session-id>.jsonl.
  Discovery reads each transcript's own recorded `cwd` rather than decoding the
  directory slug (the slug is a lossy path encoding; the record is explicit), so
  unrelated workspaces are never copied. Subagent turns are embedded in the parent
  transcript rather than emitted as separate child sessions, so a discovered file is
  the operator-driven session and is classified `primary`; `parentUuid` is a message
  pointer and is never read as session lineage. Claude Code exposes one live
  projects/ root and no archived tier, so every transcript is root_kind `active`.

After syncing, the script derives the wake-up review queue deterministically
(archived transcripts absent from digest-log.md, current session excluded, oldest
first by mtime) and decides whether a review is DUE (P-28, 2026-07-16: queue
>= REVIEW_THRESHOLD or oldest pending older than STALENESS_DAYS — every-session
mining retired as too heavy under active operator guidance). The wake-up idiom
reads this verdict instead of manually cross-referencing the archive against the
digest-log. Idempotent: lost stdout is recovered by re-running (L-24: the script
IS the state derivation).

Usage:
  python3 sync_sessions.py [--workspace PATH] [--dest PATH] [--host NAME]
                           [--current-session ID]

Defaults: workspace = git toplevel of the CWD (fallback: CWD); dest =
<workspace>/system/ops/session-store; host = all registered adapters.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

TRANSCRIPT_GLOB = "*.jsonl"
DIGEST_LOG = "digest-log.md"
LINEAGE_FILE = "lineage.json"
LINEAGE_SCHEMA = "session-lineage/v1"
CHILD_ROLES = {"subagent", "guardian"}
REVIEW_THRESHOLD = 10     # review due when this many transcripts are pending
STALENESS_DAYS = 14       # ... or when the oldest pending is older than this
SESSION_ID_RE = re.compile(r"^- ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b", re.M)
UUID_RE = re.compile(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", re.I)


# --- host adapters ---------------------------------------------------------


def _claude_code_session_roots() -> list[Path]:
    """Configured/default Claude Code project-transcript roots, de-duplicated."""
    roots = []
    configured = os.environ.get("CLAUDE_CONFIG_DIR")
    homes = [Path(configured).expanduser()] if configured else []
    homes.append(Path.home() / ".claude")
    for home in homes:
        projects = home / "projects"
        if projects.is_dir() and projects.resolve() not in roots:
            roots.append(projects.resolve())
    return roots


def _claude_code_metadata(path: Path) -> dict:
    """First record carrying session identity, without loading transcript prose."""
    try:
        with path.open() as stream:
            for line in stream:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict) and "cwd" in record:
                    return record
    except OSError:
        pass
    return {}


def discover_claude_code(workspace: Path) -> list[Path]:
    """Claude Code transcripts whose recorded cwd belongs to this workspace.

    Reads each transcript's own `cwd` rather than decoding the project-dir slug:
    the slug is a lossy path encoding, the record is explicit.
    """
    found = []
    for root in _claude_code_session_roots():
        for path in root.glob(f"*/{TRANSCRIPT_GLOB}"):
            cwd = _claude_code_metadata(path).get("cwd")
            if not isinstance(cwd, str):
                continue
            try:
                belongs_here = Path(cwd).expanduser().resolve() == workspace
            except OSError:
                belongs_here = False
            if belongs_here:
                found.append(path)
    return found


def _claude_code_lineage(path: Path) -> tuple[str, str | None]:
    """Classify only explicit Claude Code session metadata.

    Claude Code embeds subagent (sidechain) turns in the parent's own transcript
    rather than emitting separate child sessions, so a discovered file is the
    operator-driven session itself. `parentUuid` is a message pointer, never a
    session parent — it is deliberately not read as lineage.
    """
    record = _claude_code_metadata(path)
    if record.get("isSidechain") is True:
        return "subagent", None
    if record.get("userType") == "external" and record.get("sessionId"):
        return "primary", None
    return "unclassified", None


HOST_ADAPTERS = {
    "claude-code": discover_claude_code,
}


# --- sync ------------------------------------------------------------------


def default_workspace() -> Path:
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(top).resolve()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd().resolve()


def _session_id(path: Path) -> str:
    """Return a stable archive id for either supported host format."""
    matches = UUID_RE.findall(path.stem)
    if matches:
        return matches[-1].lower()
    return path.stem


def _dedupe_sources(source_files: list[tuple[str, Path]]) -> list[tuple[str, Path]]:
    """Keep the most complete source for each stable session id across host roots."""
    selected: dict[str, tuple[str, Path]] = {}
    for host, path in sorted(set(source_files), key=lambda item: (item[0], str(item[1]))):
        session_id = _session_id(path)
        current = selected.get(session_id)
        if current is None:
            selected[session_id] = (host, path)
            continue
        try:
            path_stat = path.stat()
            current_stat = current[1].stat()
            path_key = (path_stat.st_size, path_stat.st_mtime_ns, str(path))
            current_key = (current_stat.st_size, current_stat.st_mtime_ns, str(current[1]))
        except OSError:
            continue
        if path_key > current_key:
            selected[session_id] = (host, path)
    return sorted(selected.values(), key=lambda item: (item[0], str(item[1])))


def _source_root_kind(host: str, path: Path) -> str:
    """Name the explicit host root a transcript came from; never infer task role."""
    # Claude Code keeps one live projects/ root; it has no archived tier.
    return "active" if host == "claude-code" else "unknown"


def _lineage_record(host: str, path: Path) -> dict:
    role, parent = (
        _claude_code_lineage(path) if host == "claude-code" else ("unclassified", None)
    )
    return {
        "host": host,
        "root_kind": _source_root_kind(host, path),
        "role": role,
        "parent": parent,
        "basis": (
            "explicit-claude-code-metadata"
            if role != "unclassified"
            else "unsupported-or-incomplete-metadata"
        ),
    }


def _load_lineage(dest: Path) -> dict[str, dict]:
    path = dest / LINEAGE_FILE
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    if data.get("schema") == LINEAGE_SCHEMA and isinstance(data.get("sessions"), dict):
        return {
            session_id: record
            for session_id, record in data["sessions"].items()
            if isinstance(record, dict)
        }
    # Preserve the incoming branch's unversioned session inventory, but never trust its
    # relationship labels: it marked VS Code sessions primary without explicit evidence.
    if all(isinstance(value, dict) for value in data.values()):
        normalized = {}
        for session_id, record in data.items():
            host = record.get("host") if isinstance(record.get("host"), str) else "unknown"
            root_kind = record.get("root_kind")
            normalized[session_id] = {
                "host": host,
                "root_kind": root_kind if root_kind in {"active", "archived"} else "unknown",
                "role": "unclassified",
                "parent": None,
                "basis": "legacy-unproven",
            }
        return normalized
    return {}


def _write_lineage(dest: Path, sessions: dict[str, dict]) -> None:
    payload = {"schema": LINEAGE_SCHEMA, "sessions": sessions}
    (dest / LINEAGE_FILE).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _same_workspace(value: object, workspace: Path) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return Path(value).expanduser().resolve() == workspace
    except OSError:
        return False


def sync(workspace: Path, dest: Path, hosts: list[str]) -> int:
    source_files: list[tuple[str, Path]] = []
    for host in hosts:
        source_files.extend((host, path) for path in HOST_ADAPTERS[host](workspace))
    source_files = _dedupe_sources(source_files)
    if not source_files:
        print(f"WARN: no session store found for workspace {workspace} "
              f"(hosts tried: {', '.join(hosts)}) — nothing synced.")
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    lineage = _load_lineage(dest)
    copied, skipped = [], 0
    for host, src in source_files:
        session_id = _session_id(src)
        target = dest / f"{session_id}.jsonl"
        try:
            s = src.stat()
        except OSError as exc:
            print(f"WARN: cannot stat transcript {src}: {exc}")
            continue
        if target.exists():
            t = target.stat()
            if t.st_size > s.st_size:
                retained_host = lineage.get(session_id, {}).get("host", host)
                if retained_host not in HOST_ADAPTERS:
                    retained_host = host
                retained = _lineage_record(retained_host, target)
                retained["root_kind"] = lineage.get(session_id, {}).get(
                    "root_kind", _source_root_kind(host, src)
                )
                lineage[session_id] = retained
                print(f"WARN: preserving larger archived transcript {target.name} "
                      f"({t.st_size} bytes > source {s.st_size} bytes).")
                skipped += 1
                continue
            if t.st_size == s.st_size and t.st_mtime >= s.st_mtime:
                lineage[session_id] = _lineage_record(host, src)
                skipped += 1
                continue
        lineage[session_id] = _lineage_record(host, src)
        shutil.copy2(src, target)
        copied.append(target.name)
    _write_lineage(dest, lineage)
    print(f"session-store sync: {len(copied)} copied/updated, {skipped} unchanged.")
    for name in copied:
        print(f"  + {name}")
    return 0


def report_review_queue(dest: Path, current_session: str | None) -> None:
    """Derive the review queue (archived − digest-log − current) and its due-ness.

    Due (P-28): pending >= REVIEW_THRESHOLD, or oldest pending older than
    STALENESS_DAYS. Otherwise the queue accrues silently — live capture (L-3)
    covers in-session catches; full scan-mode retros also drain the queue.
    """
    import time
    digest = dest / DIGEST_LOG
    logged = set(SESSION_ID_RE.findall(digest.read_text())) if digest.is_file() else set()
    archived = {path.stem: path for path in dest.glob(TRANSCRIPT_GLOB)}
    unlogged = [
        p for p in dest.glob(TRANSCRIPT_GLOB)
        if p.stem not in logged and p.stem != current_session
    ]
    lineage = _load_lineage(dest)
    pending = []
    secondary = []
    detached_children = []
    pairings = []
    for path in unlogged:
        record = lineage.get(path.stem, {})
        role = record.get("role", "unclassified")
        parent = record.get("parent")
        can_ride = (
            role in CHILD_ROLES
            and isinstance(parent, str)
            and (parent == current_session or (parent in archived and parent not in logged))
        )
        if can_ride:
            secondary.append(path)
            pairings.append(("secondary", path.stem, parent, role))
        else:
            pending.append(path)
            if role in CHILD_ROLES:
                detached_children.append(path)
                pairings.append(("queued", path.stem, parent, role))
    notes = []
    if secondary:
        notes.append(f"+{len(secondary)} child transcript(s) as secondary evidence")
    if detached_children:
        notes.append(f"+{len(detached_children)} child transcript(s) queued normally without a pending parent")
    child_note = f" ({'; '.join(notes)})" if notes else ""
    if not pending:
        print(f"review-queue: 0 pending{child_note}.")
    else:
        pending.sort(key=lambda p: p.stat().st_mtime)
        head = pending[0]
        oldest_days = (time.time() - head.stat().st_mtime) / 86400
        reasons = []
        if len(pending) >= REVIEW_THRESHOLD:
            reasons.append(f"{len(pending)} pending >= {REVIEW_THRESHOLD}")
        if oldest_days > STALENESS_DAYS:
            reasons.append(f"oldest pending {oldest_days:.0f}d > {STALENESS_DAYS}d")
        if reasons:
            print(f"review-queue: {len(pending)} pending{child_note} · REVIEW DUE ({'; '.join(reasons)}) "
                  f"· next (oldest): {head.stem}")
        else:
            print(f"review-queue: {len(pending)} pending{child_note}, below trigger "
                  f"(<{REVIEW_THRESHOLD} and oldest {oldest_days:.0f}d <= {STALENESS_DAYS}d) "
                  f"— no review due, proceed.")
    for disposition, child, parent, role in sorted(pairings)[:20]:
        print(f"  lineage: {disposition} {child} -> {parent or 'unknown'} ({role})")
    if len(pairings) > 20:
        print(f"  lineage: ... {len(pairings) - 20} more pairing(s); use transcript.py list")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workspace", type=Path, default=None,
                    help="workspace root the transcripts belong to (default: git toplevel)")
    ap.add_argument("--dest", type=Path, default=None,
                    help="archive folder (default: <workspace>/ops/session-store)")
    ap.add_argument("--host", choices=sorted(HOST_ADAPTERS), action="append",
                    help="host adapter(s) to use (default: all registered)")
    ap.add_argument("--current-session", default=None,
                    help="session id of the running session (excluded from the review queue)")
    args = ap.parse_args()
    workspace = (args.workspace or default_workspace()).resolve()
    dest = (args.dest or workspace / "system/ops/session-store").resolve()
    hosts = args.host or sorted(HOST_ADAPTERS)
    ret = sync(workspace, dest, hosts)
    if ret == 0:
        report_review_queue(dest, args.current_session)
    return ret


if __name__ == "__main__":
    sys.exit(main())
