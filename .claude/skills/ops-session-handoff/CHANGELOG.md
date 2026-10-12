# Changelog

Notable changes to the **ops-session-handoff** package. Format:
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning:
[SemVer](https://semver.org/) via `metadata.version` in SKILL.md.

## [Unreleased]

### Changed

- Frontmatter `name:` corrected to match the package folder name (open-standard directory-match rule, meta-skill-author §validation; recipient-confirmed defect, F-2 payload item 3 / export issue #2). No behavior change.

## [0.15.0] — 2026-07-22

### Added

- Codex transcript sync now writes a private, versioned `lineage.json` manifest using
  explicit real-host metadata shapes for primary, subagent, and guardian tasks. Missing,
  incomplete, and unsupported relationships remain `unclassified`; no role is inferred
  from timestamps or paths.
- The review queue treats a proven child as secondary evidence only while its explicit
  parent is pending/current. A child whose parent is absent or already digested stays in
  the normal queue so lineage can never suppress recoverable evidence.

### Changed

- Existing unversioned lineage maps retain their session inventory but normalize every
  unproven relationship to `unclassified`; rediscovered Codex transcripts are then
  reclassified from their own explicit envelopes.
- A refused smaller/truncated source now re-derives lineage from the fuller retained
  archive, preserving metadata monotonicity together with transcript no-shrink.
- Review output and `transcript.py list` expose child-to-parent pairings, bounded in the
  sync summary, so reviewers need not inspect the private manifest by hand.
- Generic and Glean ports were re-derived at the v0.15.0 source stamp; the generic
  capability contract now carries the explicit-only lineage rule and Glean records the
  manifest as dropped-with-reason.

### Tests

- Retained all current no-shrink, active/archive, compatible-database fallback, and
  schema-degradation fixtures; added exact state-database exclusion coverage plus a
  synthetic fixture matching observed Codex parent/child/guardian metadata envelopes.
- Added queue assertions for proven secondary children, detached children, and
  unclassified sessions, plus a legacy-manifest migration regression.

## [0.14.2] — 2026-07-22

### Fixed

- Codex transcript discovery now covers both active `sessions/` and
  `archived_sessions/`, closing the archive-before-catch-up race while preserving
  workspace filtering and stable task IDs.
- A schema-tolerant, read-only `state_*.sqlite` reconciliation reports workspace
  tasks missing from the archive without making the database a content source or
  blocking rollout sync when the internal schema changes.
- Deterministic tests cover active/archive discovery, workspace isolation, non-regression
  of fuller archived content, missing index rows, compatible-database fallback, and safe
  schema-drift degradation.

## [0.14.1] — 2026-07-21

### Fixed

- The memory-drift report no longer demands live Copilot pointer stubs when the
  branch explicitly marks Copilot historical/unsupported. Machine-only Copilot
  content remains visible so untransplanted memory cannot disappear silently.
- Ports re-derived to the 0.14.1 source stamp; the portable drift rule now scopes
  host-specific mirror parity to active hosts.

---

## [0.14.0] — 2026-07-21

### Added

- **Codex generated-memory mirror** — `sync_memories.py` copies native generated
  memory one-way into a private workspace archive without editing the host store or
  pruning the mirror. Extension-owned instructions are excluded by default.
- **Session-start continuity hook contract** — a fresh Codex task catches up both the
  transcript archive and the generated-memory mirror, then routes the agent to the
  tracked repo-memory authority. The wrapper ships inside the package; the Codex
  adapter owns the trust-gated project-hook binding.

### Changed

- Ports re-derived through v0.14.0: source-version stamps and bundled-file manifests
  now cover the structured eval set plus transcript, memory-sync, reader, and drift
  scripts, with explicit dropped-with-reason handling on Glean.
- Eval set restructured (MV46 S2, eval-set v1): prose `evals/trigger-eval.md` migrated
  into structured `evals/eval-cases.yaml`; shape-clustered corpus trigger cases and
  deterministic execution cases now travel with the package.
- Bundle-lint path follows the `ops-kb-enrich` rename; eval-set v2 added the live
  handoff + next-session-goal + deferred-elicitation case, and v3 covers both continuity
  archives.
- Handoff step 6 now syncs every available host continuity archive, not only chat
  transcripts. Generated memories remain recall; tracked files remain authoritative.
- Memory drift reporting now includes stale or missing Codex generated-memory mirrors.

---

## [0.13.0] — 2026-07-21

### Added

- **Codex transcript adapter** — `sync_sessions.py` discovers append-only rollout
  JSONL under `CODEX_HOME/sessions`, filters it by `session_meta.payload.cwd`, and
  archives it under the stable task UUID so the existing digest queue remains valid.
- **Dual-format transcript reader** — `transcript.py` now normalizes Codex
  `response_item` messages alongside the existing VS Code Copilot patch stream.

### Changed

- Host adapters now return workspace-owned transcript files rather than directories;
  the VS Code Copilot adapter preserves its existing discovery behavior.
- Added postponed annotation evaluation so the sync remains usable on the current
  Codex host's Python 3.9 fallback while the workspace Python 3.10+ bootstrap is pending.

---

## [0.12.0] — 2026-07-20

### Changed
- PROGRESS structure: **Standing items** promoted to a top-level section (between
  Current milestone and Backlog / Icebox) — durable operational loops and human-only
  queue items belonging to no milestone; pointer-thin, on the cold-start critical
  path. Previously a trailing list under Current milestone. Operator decision
  2026-07-20; SKILL.md spec + both ports updated; section numbering shifts by one.

## [0.11.1] — 2026-07-20

### Fixed
- Trigger-eval set: added the parallel-thread-awareness should-trigger seed
  (recurring real shape, 2 captures 2026-07-14 — operator flags a concurrent
  agent's earlier handoff; correct behavior is re-deriving state from disk and
  folding only this thread's deltas). MV45 S3 seed-quality spot-check.

## [0.11.0] — 2026-07-14

### Added
- **`scripts/memory_drift.py`** — read-only drift report for out-of-workspace
  customization surfaces: repo-memory vs. the tracked home, workspace-mentioning
  user-scope memories with no in-repo mirror, and user/system-level Claude &
  Copilot surfaces (CLAUDE.md, rules/, skills/, user prompts, managed settings)
  that load into sessions but don't travel with the repo. Wired into workflow
  step 4; pairs with the always-on memory-sync rule (mirror-in-same-turn).
  First run surfaced 12 live findings (operator-reviewed).

## [0.10.0] — 2026-07-14

### Added
- **`scripts/sync_sessions.py`** — portable session-transcript archiver (graduated
  from `system/ops/session-store/` into the package per the exportable-unit rule): copies
  new/grown transcripts from the host's session store into the workspace archive,
  idempotently; per-host discovery adapters (`vscode-copilot` implemented,
  multi-OS user-data roots); `--workspace` / `--dest` / `--host` overrides.
- **`transcript-archive` capability** in the contract sidecar (optional tier;
  degradation: persist-at-approval discipline is the only safeguard). Workflow
  step 6 runs it at session end; the workspace wake-up idiom re-runs it at session
  start. Motivated by lesson L-22 (chat-approved roster unrecoverable from the
  session index).

## [0.9.0] — 2026-07-10

### Added
- **`evals/trigger-eval.md`** — distilled install-acceptance trigger-eval set
  (20 queries + expected verdicts, generic by construction) per meta-skill-author
  §2.1/§6. Landed 2026-07-09 with workspace milestone MV22; recorded here at the
  MV20 paste-bundle refresh.

### Changed
- **Ports re-derived** — both port manifests gain the `evals/trigger-eval.md` row
  (travels with every port); the Glean port's install steps gain the
  self-administered acceptance check; source-version stamps re-pinned.

## [0.8.0] — 2026-07-09

### Added
- **`capability-contract.yaml`** — machine-readable capability sidecar per
  meta-skill-author §4.0 (workspace lesson L-11 backfill): five optional-tier
  capabilities (durable-document-store, versioned-checkpoints, change-detection,
  script-execution, byproduct-store), each with purpose + degradation from the
  generic's contract table.
- **`compatibility` frontmatter prose** derived from the sidecar.
- **"Host capabilities required" block in `ports/glean-agent.md`** — the sidecar
  rendered against the Glean adapter's `## Provides` inventory.

## [0.7.0] — 2026-07-09

### Added
- **Distribution package retrofit.** README, this CHANGELOG, SOURCES.md (citation →
  upstream map), and semver-normalized `metadata.version` (`0.7` → `0.7.0`), required
  by the skill's `distribution-scope: "exportable"` declaration (meta-skill-author
  §1.3/§6).
- **`ports/generic.md`** — stage-1 harness/workspace-neutral canon per
  meta-skill-author §4.0: capability contract (durable documents, versioned
  checkpoints, change detection, ledger audit, hygiene audits, byproduct store),
  parameterized invocation inputs, platform-neutral bundled-file manifest.
- **`ports/glean-agent.md`** — stage-2 paste-ready Glean Agent Builder port.

### Pre-changelog history

Versions 0.1–0.7 predate this changelog; their evolution (dual-scope split at MV11,
route-then-compact, ledger reconciliation, system/ops/ byproduct sweep) is recorded in the
source workspace's git log and system/HISTORY.md and is summarized in the SKILL.md body where
each rule carries its adoption note.
