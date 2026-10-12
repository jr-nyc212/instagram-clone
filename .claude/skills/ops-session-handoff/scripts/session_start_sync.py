#!/usr/bin/env python3
"""Claude Code SessionStart hook: catch up transcripts and the host-memory mirror.

Idempotent and derived from durable state, never recollection (canon 01 wake-up idiom).
Two legs, both copy-only into the workspace:
  - transcripts -> system/ops/session-store/   (sync_sessions.py)
  - host memory -> system/ops/memory-store/claude-code/  (sync_memories.py)

Claude Code keeps both outside the repo and keyed to the workspace path, so mirroring is
what lets a handoff carry them. Per canon 04 the mirror is recall material only: the
authoritative durable guardrails are the tracked files under harness/memories/."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def repository_root(cwd: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip()).resolve()


def run_sync(command: list[str], cwd: Path, label: str) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip().splitlines()
    summary = output[0] if output else f"{label}: no output"
    if result.returncode != 0:
        detail = next(
            (line for line in reversed(output) if line.startswith(("WARN:", "ERROR:"))),
            summary,
        )
        return f"{label}: warning ({summary}; {detail})"
    return summary


def hook_output(transcript_summary: str, memory_summary: str) -> dict:
    warned = "warning" in (transcript_summary + memory_summary).lower()
    status = "finished with warnings" if warned else "completed"
    context = (
        f"Runtime-state catch-up {status}. "
        f"{transcript_summary} {memory_summary} "
        "Repository memory authority is harness/memories/README.md; "
        "load the relevant tracked guardrails before changing system behavior. "
        "Host-generated memory is recall only; tracked workspace files remain authoritative."
    )
    return {
        "suppressOutput": True,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        },
    }


def self_test() -> int:
    output = hook_output("session-store sync: ok.", "host-memory sync: ok.")
    assert output["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "harness/memories/README.md" in output["hookSpecificOutput"]["additionalContext"]
    warning = run_sync(
        [
            sys.executable,
            "-c",
            "import sys; print('host-memory sync: partial'); "
            "print('WARN: cannot mirror memory.md'); sys.exit(1)",
        ],
        Path.cwd(),
        "host-memory sync",
    )
    assert "warning" in warning and "cannot mirror memory.md" in warning
    warning_output = hook_output("session-store sync: ok.", warning)
    assert "finished with warnings" in warning_output["hookSpecificOutput"]["additionalContext"]
    print("session_start_sync self-test: PASS")
    return 0


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        return self_test()
    try:
        payload = json.load(sys.stdin)
        root = repository_root(Path(payload.get("cwd") or Path.cwd()))
        scripts = root / ".claude/skills/ops-session-handoff/scripts"
        transcript_command = [
            sys.executable,
            str(scripts / "sync_sessions.py"),
            "--workspace",
            str(root),
            "--host",
            "claude-code",
        ]
        session_id = payload.get("session_id")
        if isinstance(session_id, str) and session_id:
            transcript_command.extend(["--current-session", session_id])
        transcript_summary = run_sync(transcript_command, root, "session-store sync")
        memory_summary = run_sync(
            [
                sys.executable,
                str(scripts / "sync_memories.py"),
                "--workspace",
                str(root),
            ],
            root,
            "host-memory sync",
        )
        print(json.dumps(hook_output(transcript_summary, memory_summary)))
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(json.dumps({"systemMessage": f"Runtime-state catch-up could not run: {exc}"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
