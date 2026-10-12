#!/usr/bin/env python3
"""Read archived chat-session transcripts (system/ops/session-store/*.jsonl).

Part of the ops-session-handoff skill (transcript-archive capability), sibling of
sync_sessions.py which owns the archive itself. Promoted after the same parser was
improvised three times (L-22 roster recovery, retro-5 mining, the 2026-07-14 wake-up
review — lesson L-26): mining passes, phrasing harvests, and forensic recoveries all
need the same three reads, so they live here durably.

Transcript format — Claude Code: append-only typed records; `user`/`assistant`
records carry the conversation, `ai-title` names the session, and sidechain
(subagent) records are skipped as delegated work rather than operator turns.

Read-only — the archive is never-hand-edit.

Subcommands:
  list                     id · date · lineage · title · user-turn count
  turns <session-id>       numbered user turns (phrasing harvest / wake-up review)
  grep <pattern> [id ...]  regex search over user turns + assistant prose, bounded

Usage:
  python3 transcript.py [--store PATH] list
  python3 transcript.py [--store PATH] turns <session-id> [--full]
  python3 transcript.py [--store PATH] grep <pattern> [session-id ...] [--max N]

Defaults: store = <git toplevel>/system/ops/session-store. Session ids may be abbreviated
to any unique prefix. Output is truncated (not --full) to keep it context-friendly.
"""

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

import sync_sessions

TRANSCRIPT_GLOB = "*.jsonl"
TRUNC = 1200


# --- parsing ----------------------------------------------------------------


def default_store() -> Path:
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(top) / "system/ops/session-store"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd() / "system/ops/session-store"


def _parse_iso_timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _claude_text(content) -> str:
    """Prose from a Claude Code message body, skipping thinking and tool blocks."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = [
        block.get("text", "")
        for block in content
        if isinstance(block, dict)
        and block.get("type") == "text"
        and isinstance(block.get("text"), str)
    ]
    return "\n\n".join(part for part in parts if part)


def _load_claude_code_session(path: Path) -> dict:
    """Extract session metadata and conversational turns from a Claude Code transcript.

    Sidechain (subagent) records are skipped: they are the parent session's
    delegated work, not operator turns, and including them would double-count the
    conversation the review queue reasons about.
    """
    session_id = path.stem
    title = ""
    created = None
    turns: list[dict] = []
    current = None
    with path.open() as stream:
        for line in stream:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict):
                continue
            if record.get("type") == "ai-title" and not title:
                candidate = record.get("aiTitle")
                if isinstance(candidate, str):
                    title = candidate
                continue
            if record.get("type") not in ("user", "assistant"):
                continue
            if record.get("isSidechain") is True or record.get("isMeta") is True:
                continue
            if created is None:
                created = _parse_iso_timestamp(record.get("timestamp"))
            message = record.get("message")
            if not isinstance(message, dict):
                continue
            text = _claude_text(message.get("content"))
            if not text:
                continue
            if record.get("type") == "user":
                current = {"i": len(turns), "user": text, "assistant": []}
                turns.append(current)
            elif current is not None:
                current["assistant"].append(text)
    return {
        "id": session_id,
        "title": title or "Claude Code session",
        "created": created,
        "turns": turns,
    }


def load_session(path: Path) -> dict:
    """Detect the host envelope and return normalized metadata + turns."""
    with path.open() as stream:
        for line in stream:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            return _load_claude_code_session(path)
    return {"id": path.stem, "title": "", "created": None, "turns": []}


def resolve_ids(store: Path, prefixes: list[str]) -> list[Path]:
    """Map (possibly abbreviated) session ids to transcript paths."""
    all_paths = sorted(store.glob(TRANSCRIPT_GLOB))
    if not prefixes:
        return all_paths
    out = []
    for prefix in prefixes:
        matches = [p for p in all_paths if p.stem.startswith(prefix)]
        if not matches:
            sys.exit(f"ERROR: no transcript matches '{prefix}' in {store}")
        if len(matches) > 1:
            sys.exit(f"ERROR: '{prefix}' is ambiguous: "
                     + ", ".join(p.stem for p in matches))
        out.append(matches[0])
    return out


def clip(text: str, full: bool) -> str:
    text = text.strip()
    if full or len(text) <= TRUNC:
        return text
    return text[:TRUNC] + f" …[+{len(text) - TRUNC} chars]"


# --- subcommands -------------------------------------------------------------


def cmd_list(store: Path, _args) -> int:
    rows = []
    lineage = sync_sessions._load_lineage(store)
    for path in sorted(store.glob(TRANSCRIPT_GLOB)):
        s = load_session(path)
        created = s["created"].strftime("%Y-%m-%d %H:%M") if s["created"] else "?"
        record = lineage.get(path.stem, {})
        role = record.get("role", "unclassified")
        parent = record.get("parent")
        relation = f"{role} -> {parent}" if parent else role
        rows.append((created, s["id"], len(s["turns"]), relation, s["title"]))
    rows.sort()
    for created, sid, nturns, relation, title in rows:
        print(f"{created} · {sid} · {nturns:3d} turns · {relation} · {title}")
    print(f"({len(rows)} transcripts in {store})")
    return 0


def cmd_turns(store: Path, args) -> int:
    path = resolve_ids(store, [args.session_id])[0]
    s = load_session(path)
    print(f"# {s['id']} · {s['title']} · {len(s['turns'])} user turns")
    for t in s["turns"]:
        print(f"--- turn {t['i']} ---")
        print(clip(t["user"], args.full) or "(empty)")
    return 0


def cmd_grep(store: Path, args) -> int:
    pattern = re.compile(args.pattern, re.IGNORECASE)
    paths = resolve_ids(store, args.session_ids)
    shown = 0
    for path in paths:
        s = load_session(path)
        for t in s["turns"]:
            texts = [("user", t["user"])] + [("assistant", a) for a in t["assistant"]]
            for role, text in texts:
                if not text or not pattern.search(text):
                    continue
                m = pattern.search(text)
                lo, hi = max(0, m.start() - 120), min(len(text), m.end() + 120)
                print(f"{s['id'][:8]} · turn {t['i']} · {role}: …{text[lo:hi].strip()}…")
                shown += 1
                if shown >= args.max:
                    print(f"(stopped at --max {args.max})")
                    return 0
                break  # one hit per text is enough
    print(f"({shown} match(es))")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--store", type=Path, default=None,
                    help="archive folder (default: <git toplevel>/system/ops/session-store)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="id · date · title · user-turn count")

    p_turns = sub.add_parser("turns", help="print a session's user turns")
    p_turns.add_argument("session_id", help="session id (unique prefix ok)")
    p_turns.add_argument("--full", action="store_true",
                         help="no truncation (default clips long turns)")

    p_grep = sub.add_parser("grep", help="regex search user turns + assistant prose")
    p_grep.add_argument("pattern")
    p_grep.add_argument("session_ids", nargs="*",
                        help="restrict to these sessions (default: whole archive)")
    p_grep.add_argument("--max", type=int, default=40, help="match cap (default 40)")

    args = ap.parse_args()
    store = (args.store or default_store()).resolve()
    if not store.is_dir():
        sys.exit(f"ERROR: store not found: {store}")
    return {"list": cmd_list, "turns": cmd_turns, "grep": cmd_grep}[args.cmd](store, args)


if __name__ == "__main__":
    sys.exit(main())
