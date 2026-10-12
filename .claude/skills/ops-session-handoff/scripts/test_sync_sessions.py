#!/usr/bin/env python3
"""Deterministic tests for Claude Code transcript discovery and reconciliation.

Covers the host-neutral invariants the archive depends on — workspace-bound
discovery, most-complete-copy dedupe, the no-shrink guard, explicit-only lineage,
and legacy-manifest rewriting — against real Claude Code transcript shape.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sync_sessions
import transcript


WORKSPACE_ID = "11111111-1111-1111-1111-111111111111"
SECOND_ID = "22222222-2222-2222-2222-222222222222"
FOREIGN_ID = "33333333-3333-3333-3333-333333333333"
LEGACY_ID = "44444444-4444-4444-4444-444444444444"
CHILD_ID = "55555555-5555-5555-5555-555555555555"
SIDECHAIN_ID = "66666666-6666-6666-6666-666666666666"


def slug(path: Path) -> str:
    """Claude Code's project-dir encoding: absolute path with separators hyphenated."""
    return str(path).replace("/", "-")


def write_transcript(
    path: Path,
    session_id: str,
    cwd: Path,
    *,
    user_type: str = "external",
    sidechain: bool = False,
    extra_lines: str = "",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    head = {"type": "mode", "sessionId": session_id}
    first = {
        "type": "user",
        "cwd": str(cwd),
        "sessionId": session_id,
        "parentUuid": None,
        "userType": user_type,
        "isSidechain": sidechain,
    }
    path.write_text(json.dumps(head) + "\n" + json.dumps(first) + "\n" + extra_lines)


class ClaudeCodeSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.workspace = (self.root / "workspace").resolve()
        self.workspace.mkdir()
        self.config = (self.root / "claude-home").resolve()
        (self.config / "projects").mkdir(parents=True)
        self.environment = mock.patch.dict(
            os.environ, {"CLAUDE_CONFIG_DIR": str(self.config)}
        )
        self.environment.start()

    def tearDown(self) -> None:
        self.environment.stop()
        self.tempdir.cleanup()

    def project_dir(self, cwd: Path) -> Path:
        return self.config / "projects" / slug(cwd)

    # --- discovery ---------------------------------------------------------

    def test_discovery_is_bound_to_this_workspace(self) -> None:
        mine = self.project_dir(self.workspace) / f"{WORKSPACE_ID}.jsonl"
        also_mine = self.project_dir(self.workspace) / f"{SECOND_ID}.jsonl"
        other = self.root / "other-workspace"
        foreign = self.project_dir(other) / f"{FOREIGN_ID}.jsonl"
        write_transcript(mine, WORKSPACE_ID, self.workspace)
        write_transcript(also_mine, SECOND_ID, self.workspace)
        write_transcript(foreign, FOREIGN_ID, other)

        found = set(sync_sessions.discover_claude_code(self.workspace))

        self.assertEqual(found, {mine, also_mine})

    def test_discovery_trusts_recorded_cwd_over_directory_slug(self) -> None:
        """A transcript filed under a stale slug still binds by its recorded cwd."""
        misfiled = self.project_dir(self.root / "renamed-away") / f"{WORKSPACE_ID}.jsonl"
        write_transcript(misfiled, WORKSPACE_ID, self.workspace)

        found = sync_sessions.discover_claude_code(self.workspace)

        self.assertEqual(found, [misfiled])

    def test_transcript_without_cwd_is_ignored(self) -> None:
        headless = self.project_dir(self.workspace) / f"{WORKSPACE_ID}.jsonl"
        headless.parent.mkdir(parents=True, exist_ok=True)
        headless.write_text(json.dumps({"type": "mode", "sessionId": WORKSPACE_ID}) + "\n")

        self.assertEqual(sync_sessions.discover_claude_code(self.workspace), [])

    # --- sync invariants ---------------------------------------------------

    def test_sync_prefers_the_most_complete_copy(self) -> None:
        short = self.project_dir(self.root / "stale-slug") / f"{WORKSPACE_ID}.jsonl"
        full = self.project_dir(self.workspace) / f"{WORKSPACE_ID}.jsonl"
        write_transcript(short, WORKSPACE_ID, self.workspace, extra_lines='{"source":"short"}\n')
        write_transcript(
            full, WORKSPACE_ID, self.workspace,
            extra_lines='{"source":"full"}\n{"more":"content"}\n',
        )
        destination = self.root / "session-store"

        with contextlib.redirect_stdout(io.StringIO()):
            result = sync_sessions.sync(self.workspace, destination, ["claude-code"])

        self.assertEqual(result, 0)
        copied = (destination / f"{WORKSPACE_ID}.jsonl").read_text()
        self.assertIn('"source":"full"', copied)
        self.assertNotIn('"source":"short"', copied)

    def test_sync_never_shrinks_an_archived_transcript(self) -> None:
        live = self.project_dir(self.workspace) / f"{WORKSPACE_ID}.jsonl"
        write_transcript(live, WORKSPACE_ID, self.workspace)
        destination = self.root / "session-store"
        destination.mkdir()
        archived = destination / f"{WORKSPACE_ID}.jsonl"
        write_transcript(
            archived, WORKSPACE_ID, self.workspace,
            extra_lines='{"preserve":"finalized tail"}\n',
        )

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = sync_sessions.sync(self.workspace, destination, ["claude-code"])

        self.assertEqual(result, 0)
        self.assertIn('"preserve":"finalized tail"', archived.read_text())
        self.assertIn("preserving larger archived transcript", output.getvalue())

    # --- lineage -----------------------------------------------------------

    def test_lineage_records_primary_from_explicit_metadata(self) -> None:
        live = self.project_dir(self.workspace) / f"{WORKSPACE_ID}.jsonl"
        write_transcript(live, WORKSPACE_ID, self.workspace)
        destination = self.root / "session-store"

        with contextlib.redirect_stdout(io.StringIO()):
            sync_sessions.sync(self.workspace, destination, ["claude-code"])

        manifest = json.loads((destination / sync_sessions.LINEAGE_FILE).read_text())
        self.assertEqual(manifest["schema"], sync_sessions.LINEAGE_SCHEMA)
        self.assertEqual(
            manifest["sessions"][WORKSPACE_ID],
            {
                "basis": "explicit-claude-code-metadata",
                "host": "claude-code",
                "parent": None,
                "role": "primary",
                "root_kind": "active",
            },
        )

    def test_sidechain_transcript_is_classified_subagent_without_inferring_a_parent(self) -> None:
        """parentUuid is a message pointer, never session lineage — parent stays None."""
        side = self.project_dir(self.workspace) / f"{SIDECHAIN_ID}.jsonl"
        write_transcript(side, SIDECHAIN_ID, self.workspace, sidechain=True)
        destination = self.root / "session-store"

        with contextlib.redirect_stdout(io.StringIO()):
            sync_sessions.sync(self.workspace, destination, ["claude-code"])

        record = json.loads(
            (destination / sync_sessions.LINEAGE_FILE).read_text()
        )["sessions"][SIDECHAIN_ID]
        self.assertEqual(record["role"], "subagent")
        self.assertIsNone(record["parent"])

    def test_unrecognised_metadata_stays_unclassified(self) -> None:
        odd = self.project_dir(self.workspace) / f"{CHILD_ID}.jsonl"
        write_transcript(odd, CHILD_ID, self.workspace, user_type="internal")
        destination = self.root / "session-store"

        with contextlib.redirect_stdout(io.StringIO()):
            sync_sessions.sync(self.workspace, destination, ["claude-code"])

        record = json.loads(
            (destination / sync_sessions.LINEAGE_FILE).read_text()
        )["sessions"][CHILD_ID]
        self.assertEqual(record["role"], "unclassified")
        self.assertEqual(record["basis"], "unsupported-or-incomplete-metadata")

    def test_legacy_lineage_map_is_read_and_rewritten_with_a_schema(self) -> None:
        live = self.project_dir(self.workspace) / f"{WORKSPACE_ID}.jsonl"
        write_transcript(live, WORKSPACE_ID, self.workspace)
        destination = self.root / "session-store"
        destination.mkdir()
        legacy = {
            LEGACY_ID: {
                "host": "vscode-copilot",
                "root_kind": "active",
                "role": "primary",
                "parent": None,
            }
        }
        (destination / sync_sessions.LINEAGE_FILE).write_text(json.dumps(legacy))

        with contextlib.redirect_stdout(io.StringIO()):
            result = sync_sessions.sync(self.workspace, destination, ["claude-code"])

        self.assertEqual(result, 0)
        manifest = json.loads((destination / sync_sessions.LINEAGE_FILE).read_text())
        self.assertEqual(manifest["schema"], sync_sessions.LINEAGE_SCHEMA)
        self.assertEqual(manifest["sessions"][LEGACY_ID]["role"], "unclassified")
        self.assertEqual(manifest["sessions"][LEGACY_ID]["basis"], "legacy-unproven")

    # --- review queue / transcript view ------------------------------------

    def test_review_queue_excludes_the_current_session(self) -> None:
        first = self.project_dir(self.workspace) / f"{WORKSPACE_ID}.jsonl"
        second = self.project_dir(self.workspace) / f"{SECOND_ID}.jsonl"
        write_transcript(first, WORKSPACE_ID, self.workspace)
        write_transcript(second, SECOND_ID, self.workspace)
        destination = self.root / "session-store"

        with contextlib.redirect_stdout(io.StringIO()):
            sync_sessions.sync(self.workspace, destination, ["claude-code"])

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            sync_sessions.report_review_queue(destination, SECOND_ID)

        self.assertIn("review-queue: 1 pending", output.getvalue())

    def test_transcript_list_exposes_child_parent_pairing(self) -> None:
        destination = self.root / "session-store"
        destination.mkdir()
        write_transcript(destination / f"{CHILD_ID}.jsonl", CHILD_ID, self.workspace)
        payload = {
            "schema": sync_sessions.LINEAGE_SCHEMA,
            "sessions": {
                CHILD_ID: {
                    "basis": "explicit-claude-code-metadata",
                    "host": "claude-code",
                    "root_kind": "active",
                    "role": "subagent",
                    "parent": WORKSPACE_ID,
                }
            },
        }
        (destination / sync_sessions.LINEAGE_FILE).write_text(json.dumps(payload))

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = transcript.cmd_list(destination, None)

        self.assertEqual(result, 0)
        self.assertIn(f"subagent -> {WORKSPACE_ID}", output.getvalue())


if __name__ == "__main__":
    unittest.main()
