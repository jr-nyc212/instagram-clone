#!/usr/bin/env python3
"""Mirror generated host memory state into a private workspace archive.

Claude Code keeps per-project memory outside the repo, at
<CLAUDE_CONFIG_DIR|~/.claude>/projects/<slugified-workspace>/memory/ — so it is keyed to
the workspace path and does NOT survive a clone or a move. This mirror copies it into the
workspace (system/ops/memory-store/claude-code/, gitignored) so a handoff carries it.

Per canon 04 the mirror is recall material, never authority: the tracked guardrails in
harness/memories/ remain canonical. The host source is authoritative for its own state and
is never edited; the mirror is copy-only, so source deletions are retained until a human
explicitly prunes the workspace archive.

Usage: python3 sync_memories.py [--workspace PATH] [--source PATH] [--dest PATH]
Exit code: 0 when the source is absent or the mirror is current; 1 on copy errors.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXCLUDED_TOP_LEVEL = {"extensions"}


def default_workspace() -> Path:
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return Path(top).resolve()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd().resolve()


def _config_home() -> Path:
    configured = os.environ.get("CLAUDE_CONFIG_DIR")
    return (Path(configured).expanduser() if configured else Path.home() / ".claude")


def project_slug(workspace: Path) -> str:
    """Claude Code's project-dir encoding: absolute path with separators hyphenated."""
    return str(workspace).replace("/", "-")


def default_source(workspace: Path | None = None) -> Path:
    """This workspace's Claude Code memory directory.

    Honours the autoMemoryDirectory setting when present, since that relocates the
    store away from the default project path.
    """
    workspace = (workspace or repository_root(Path.cwd())).resolve()
    for settings_name in ("settings.local.json", "settings.json"):
        settings = workspace / ".claude" / settings_name
        if not settings.is_file():
            continue
        try:
            configured = json.loads(settings.read_text()).get("autoMemoryDirectory")
        except (OSError, json.JSONDecodeError):
            configured = None
        if isinstance(configured, str) and configured:
            return Path(configured).expanduser().resolve()
    return (_config_home() / "projects" / project_slug(workspace) / "memory").resolve()


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def source_files(source: Path, include_extensions: bool = False) -> list[Path]:
    if not source.is_dir():
        return []
    files = []
    for path in source.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(source)
        if not include_extensions and relative.parts[0] in EXCLUDED_TOP_LEVEL:
            continue
        files.append(path)
    return sorted(files)


def sync(source: Path, dest: Path, include_extensions: bool = False) -> tuple[int, int, list[str]]:
    if not source.is_dir():
        print(f"host-memory sync: source missing ({source}) — nothing synced.")
        return 0, 0, []
    try:
        dest.relative_to(source)
    except ValueError:
        pass
    else:
        raise ValueError("memory mirror destination cannot be inside the host source store")

    copied: list[str] = []
    unchanged = 0
    failures: list[str] = []
    dest.mkdir(parents=True, exist_ok=True)
    for src in source_files(source, include_extensions):
        relative = src.relative_to(source)
        target = dest / relative
        try:
            if target.is_file() and target.stat().st_size == src.stat().st_size:
                if digest(target) == digest(src):
                    unchanged += 1
                    continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            copied.append(relative.as_posix())
        except OSError as exc:
            failures.append(f"{relative.as_posix()}: {exc}")

    print(f"host-memory sync: {len(copied)} copied/updated, {unchanged} unchanged.")
    for name in copied:
        print(f"  + {name}")
    for detail in failures:
        print(f"WARN: cannot mirror {detail}")
    return len(copied), unchanged, failures


def self_test() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        source = root / "source"
        dest = root / "dest"
        source.mkdir()
        (source / "memory.md").write_text("one\n")
        extension = source / "extensions/chronicle"
        extension.mkdir(parents=True)
        (extension / "instructions.md").write_text("extension\n")
        copied, unchanged, failures = sync(source, dest)
        assert (copied, unchanged, failures) == (1, 0, [])
        assert (dest / "memory.md").read_text() == "one\n"
        assert not (dest / "extensions").exists()
        copied, unchanged, failures = sync(source, dest)
        assert (copied, unchanged, failures) == (0, 1, [])
        (source / "memory.md").write_text("two\n")
        copied, unchanged, failures = sync(source, dest)
        assert (copied, unchanged, failures) == (1, 0, [])
        assert (dest / "memory.md").read_text() == "two\n"
        (source / "memory.md").unlink()
        copied, unchanged, failures = sync(source, dest)
        assert (copied, unchanged, failures) == (0, 0, [])
        assert (dest / "memory.md").read_text() == "two\n"
    print("sync_memories self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--dest", type=Path, default=None)
    parser.add_argument("--include-extensions", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    workspace = (args.workspace or default_workspace()).resolve()
    source = (args.source or default_source(workspace)).resolve()
    dest = (args.dest or workspace / "system/ops/memory-store/claude-code").resolve()
    try:
        _, _, failures = sync(source, dest, args.include_extensions)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
