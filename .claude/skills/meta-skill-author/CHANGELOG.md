# Changelog

All notable changes to the **meta-skill-author** package are recorded here.

## [Unreleased]

### Changed

- Frontmatter `name:` corrected to match the package folder name (open-standard directory-match rule, meta-skill-author §validation; recipient-confirmed defect, F-2 payload item 3 / export issue #2). No behavior change.
- Ports re-derived (Glean refresh 2026-07-31, no semver bump): generic.md caught up
  v1.14.0 → v1.20.0 — output-first eval doctrine folded in (uplift/preference
  classification, known-good oracle, typed failure categories, diagnostic-only
  trajectory grading), eval-set graduation into the package, manifest completed
  (capability-vocabulary.md, decision-sequence.md, eval.sh backfilled);
  glean-agent.md re-stamped to v1.20.0 (the 1.20 delta is eval-backend vocabulary
  with no Glean-side effect).

## [1.20.0] — 2026-07-21

### Changed

- Added neutral `agent-cli-subprocess` capability vocabulary for the Codex-native
  eval backend; retained `copilot-cli-subprocess` as a historical identifier only.

### Changed

- Ports re-derived (Glean bundle refresh 2026-07-20): glean-agent.md caught up to
  v1.19.0 — the shared-agent acceptance-query discipline now carries the
  output-first eval doctrine (deterministic-bias checks, known-good example);
  both manifests name `evals/eval-cases.yaml` (trigger-eval.md retired).

### Changed

- Eval set restructured (MV46 S2, eval-set v1 — no skill semver bump): prose `evals/trigger-eval.md` migrated into structured `evals/eval-cases.yaml` (schema: meta-skill-eval references); corpus-sourced trigger cases from real archive phrasings + a deterministic execution case added. The prose set lives in git history before the S2 commit.
- Eval set v2 (no semver bump): live-capture near-miss c04 — recurring mechanical-rename shape, correctly executed inline below authoring-mode threshold (C19 coverage).

## [1.19.0] — 2026-07-20

### Changed

- Eval authoring is explicitly output-first: optional capability-uplift vs
  encoded-preference classification, known-good oracle required where deterministic
  artifact verification is feasible, typed output-failure categories, and parsimonious
  distinct checks.
- Trajectory/single-step evaluation is diagnostic (failures, surprising passes,
  graduation, model/harness changes) and stops at failure-class saturation; paired
  skill-vs-masked output uplift routes to `meta-skill-eval report --paired`.
- Fixed pre-existing package version drift: capability contract 1.17.0 → 1.19.0 to
  match SKILL.md/changelog lineage.

## [1.18.0] — 2026-07-20

### Changed

- **Eval execution routed to `meta-skill-eval`** (MV46 S4): §2.1/§2.3 keep the
  authoring *method* (description-optimization loop, three-tier frame,
  graduation semantics) but execution — runs, trials, transcript-derived
  verdicts, the graduation/saturation/retirement lifecycle — now reads from the
  harness skill's attributed ledger at `system/ops/evals/`, never asserted.
- Package-layout references updated §1.3/§2.1/§6: `evals/trigger-eval.md` →
  structured `evals/eval-cases.yaml` (install acceptance = self-administering
  the trigger cases; the full set runs as a program via meta-skill-eval).
- `references/capability-vocabulary.md`: new v1 capability ID
  `copilot-cli-subprocess` (the eval harness's run-mode dependency).

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
the package uses [Semantic Versioning](https://semver.org/). Because the package
ships a refresher helper skill, version history is a user-facing surface: it tells
a consumer whether they are on a stale snapshot of the research corpus. The
refresher writes internal audit-log entries during Apply mode; this file is the
human-readable public record derived from them.

When the refresher applies an approved change, add an entry under a new version
heading. A change to any of the five foundational findings (see `README.md`) is a
**minor** bump at minimum; a change that alters a published rule's meaning is
**minor**; a breaking restructure of the package layout is **major**.

---

## [1.17.0] — 2026-07-20

### Added
- **Three capability IDs** in `references/capability-vocabulary.md` —
  `browser-automation`, `image-text-extraction`, `generated-media-pipeline`
  (MV42 scope 1, plan `system/plans/capability-matrix.md`): the externally-satisfied
  capabilities the workspace's domain/tool skills lean on, needed by the
  system-contract `capability_matrix` so consuming agents can grade host fit for the
  whole installed set. Gated-change checklist run: all existing sidecars unaffected
  (none declare them); adapter Provides tables unchanged (bindings land MV42 scope 5).
  Note: the plan's draft `internal-corpus-search` was **not** added — existing
  `internal-document-search` ("workspace files or indexed org content") already
  covers it; the matrix uses the existing ID.
- **`transcript-archive` backfilled** into the vocabulary — the ops-session-handoff
  sidecar has declared it since MV27 but it never entered the controlled list
  (drift found by the MV42 matrix-consistency pass).

## [1.16.0] — 2026-07-13

### Added
- **`live-web-retrieval` capability ID** in `references/capability-vocabulary.md` —
  search + fetch over public web sources. First consumer: the `company-research`
  skill (the first exportable skill whose evidence base is live public research).
  Gated-change checklist run: all existing sidecars unaffected (none declare it);
  all six adapter Provides tables extended with the new row (claude/copilot/
  perplexity native; codex/cursor/glean partial with verify notes).

## [1.15.0] — 2026-07-11

The §2.1 optimization-loop harness becomes real: the blind-administration scripts
proven in the first full 25-skill workspace run (98.2% blind run 1; held-out
re-test 120/120) are generalized into the package, replacing the phantom
`scripts/run_loop` CLI the method text had referenced since import.

### Added
- **`scripts/prep_eval_loop.py`** — builds roster, answer key, and shuffled blind
  batches (opaque post-shuffle ids) from a directory of skill packages' distilled
  `evals/trigger-eval.md` sets; `--skills` scopes seam-scoped re-runs after roster
  changes. Parametrized, zero workspace bindings.
- **`scripts/score_run.py`** — Comparator-role scorer (`qid -> verdict` lines
  against the answer key; majority rule across multiple runs).

### Changed
- **SKILL.md §2.1** and **`references/decision-sequence.md` Step 5** — the phantom
  `python -m scripts.run_loop …` CLI replaced with the real two-script blind
  protocol; §2.1 now names the seam-scoped re-run rule (collisions are born at
  boundary edits).
- **`ports/generic.md`** bundled-file manifest — `scripts/run_loop` row corrected
  to the real script names.

---

## [1.14.0] — 2026-07-10

Port re-derivation at the MV20 Glean paste-bundle refresh — the package's own
ports catch up to rules 1.11.0–1.13.0 and the MV22 eval-set addition.

### Added
- **`evals/trigger-eval.md`** — this package's own distilled install-acceptance
  set (§2.1/§6). Landed 2026-07-09 with workspace milestone MV22; recorded here
  at the refresh.

### Changed
- **`ports/glean-agent.md`** re-derived against v1.14.0 (was stamped v1.10.0):
  manifest gains the `evals/trigger-eval.md` travels-with-the-port row; install
  steps gain the self-administered acceptance check; Design-mode sharing-scope
  gate carries the §2.1/§6 discipline as an **acceptance query set** for shared
  agents; stale `scripts/run_loop` manifest row corrected to `scripts/eval.sh`.
- **`ports/generic.md`** — manifest gains the same evals row; source-version
  stamp re-pinned.

## [1.13.0] — 2026-07-09

Vocabulary split by scale (MV23/E20 `vocab-split` scope, operator-gated). The
workspace consolidated its system-scale portability pair (`harness-generalizer` +
`onboarding-adapter`) into `meta-harness-author`; wiring-scale capability IDs move
to that skill so each vocabulary lives with the skill that owns its scale.
Published-rule meaning change (vocabulary ownership) → minor bump.

### Changed
- **`references/capability-vocabulary.md`** — the §Wiring/activation IDs (v2)
  section moved to `meta-harness-author/references/wiring-vocabulary.md`; a
  pointer remains. This file now carries skill-scale (v1) IDs only. Sidecars are
  unaffected (none declare v2 IDs — verified at the split). Wiring rows may
  declare IDs from either list; requires × provides matching unchanged.
- **SKILL.md §4.0** — the two-stage port's workspace-scale mirror now names
  `meta-harness-author`'s generalize → adapt arc (formerly the
  harness-generalizer → onboarding-adapter pair). §4.2's wiring-ID grading note
  points to the new v2 home.

---

## [1.12.0] — 2026-07-09

Trigger-eval sets become part of the exportable-skill package (MV22
`method-amendment` scope). Receiving tenants previously had no way to verify a
ported skill still triggers — eval material was authoring-time-only and lived
outside the export surface. Published-rule meaning change → minor bump.

### Added
- **SKILL.md §2.1 — graduation rule**: for exportable skills, the finished
  description-optimization set is distilled into `evals/trigger-eval.md` inside
  the package — query + expected verdict (trigger / abstain / route-to-sibling),
  self-administrable by a receiving agent without a runner.
- **SKILL.md §2.1 — generic-by-construction rule**: exportable eval sets are
  user-content-free from the first draft (internal set = shipped set; no
  sanitization step). Live capture corpora seed intent shapes but never travel
  verbatim; phrasings are specific-but-fictional.
- **SKILL.md §6 — layout + install acceptance**: `evals/trigger-eval.md` joins
  the exportable standard layout (alongside `capability-contract.yaml`); a
  receiving-agent protocol administers it post-install. Triggering conformance
  only — behavioral conformance remains the declared §4.0 gap. Separability
  audit covers the eval file; the capability sidecar may point to it, never
  restate it.
- **`scripts/eval.sh`**: gate now requires `evals/trigger-eval.md` (present +
  placeholder-free) when the target ships `capability-contract.yaml`; DoD line
  added. Sibling-workspace model unchanged for iteration residue.
- **`templates/eval-query-set.md`**: specific-but-fictional constraint for
  exportable skills + graduation step (7).

### Changed
- **`scripts/validate.sh`**: package-link check alternation extended with
  `evals/` so SKILL.md references to the new standard file are link-checked.

---

## [1.11.0] — 2026-07-09

Wiring/activation vocabulary extension (MV21 Phase 1). The system self-description
contract (`harness/system-contract.yaml`) needs controlled IDs for the eight
harness-wiring categories; keeping them in the one capability vocabulary keeps
requires × provides matching uniform across skill sidecars and adapter inventories.
Research-cited design gate (MV21 Phase R): closed-enum-in-open-array discipline from
Archon's `requires:` gate; the 08 policy-filter ID from corpus [policy-as-data];
naming follows the v1 host-capability noun-phrase style.

### Added
- **`references/capability-vocabulary.md` §Wiring/activation IDs (v2)** — five new
  system-level IDs: `always-on-instruction-injection` (canon 01),
  `path-scoped-rule-injection` (02), `scoped-memory-store` (04),
  `skill-package-discovery` (05), `native-permission-enforcement` (08, optional tier,
  upgrade-direction degradation). Canon rows 03/06/07 reuse existing v1 IDs — recorded
  in the section, settled at the Phase 1 gate.

### Checked
- All four exportable sidecars and all six adapter `## Provides` inventories re-checked
  against the extended list — no changes required (sidecars declare skill-level IDs
  only; wiring-ID grades enter adapters at their next refresh per the re-check ≠ extend
  rule).

---

## [1.10.0] — 2026-07-09

Machine-readable capability contracts for exportable skills (workspace lesson L-11:
ports carried host-capability dependencies only as prose install steps — an installer
on another platform got no "you need internal-document search" flag). No ecosystem
standard exists (research survey, 2026-07-09); field naming aligns with the closest
shipped shapes (environment-manifest `required`/`purpose`/`install_hint`, contract-spec
`recovery`→`degradation`, MCPB compatibility blocks) so the schema is
publication-ready, but it is published nowhere.

### Added
- **`references/capability-vocabulary.md`** — the controlled capability-ID vocabulary
  (11 IDs, seeded only from the four exportable generics' contract tables) + the
  `capability-contract.yaml` schema (schema-version 1). ID changes are gated package
  changes.
- **§4.0 sidecar rule.** Stage-1 Generalize emits `capability-contract.yaml` at the
  exportable skill's root — canonical; the generic's contract table, SKILL.md
  `compatibility` prose, and port capability blocks are derived from it. Known
  limitation noted: authoring-time declaration only, behavioral conformance deferred.
- **§4.2 requires × provides mapping.** Adapters carry a `## Provides` inventory
  (capability-id → native / partial / absent); every stage-2 port maps each contract
  row against it and renders a "Host capabilities required" prose block — unmet
  required ⇒ "do not install without", unmet optional ⇒ degradation note.
  `adapters/glean.md` carries the first Provides inventory.
- **§1.3 exportable row** now names `capability-contract.yaml` as a day-one package
  requirement; `scripts/validate.sh` Category 7 checks sidecar presence/shape (FAIL)
  and vocabulary membership (WARN) for exportable skills.
- **Own sidecar + `compatibility` frontmatter** — this package now carries the
  contract it prescribes.

## [1.9.1] — 2026-07-09

### Added
- **§1.3 scope-declaration home.** The distribution-scope answer is recorded as
  `metadata.distribution-scope: "internal" | "exportable"` in the skill's own
  frontmatter (travels with the skill; no registry to drift). Chosen over a
  skills-README column at the scope-backfill decision gate.
- **`ports/generic.md` (stage-1 self-port).** The package's own harness-neutral
  generic, backfilled per §4.0 alongside the other three Glean-ported skills.
- **`metadata.version` in SKILL.md frontmatter.** The package version now travels in
  the frontmatter as well as this changelog — flagged by the new workspace audit
  (C14: exportable skills must carry an explicit version).

## [1.9.0] — 2026-07-09

### Added
- **§1.3 distribution-scope declaration.** The spec gate now requires asking the human
  whether the skill is **internal** (lean layout; git + workspace changelog as version
  history; workspace bindings allowed) or **exportable** (full §6 distribution package +
  separability bar + capability-contract bindings from day one). Undeclared scope
  defaults to internal; a later export must run §4.0 stage-1 Generalize first. §6 now
  states it applies only to exportable skills. Rationale: scaffolding scales with
  distribution distance, not importance — previously implicit, so the two workflows
  were followed inconsistently.

---

## [1.8.0] — 2026-07-09

### Added
- **§4.0 Two-stage port: Generalize → Apply.** Port mode is now explicitly two stages:
  stage 1 produces `ports/generic.md` (workspace/harness-neutral canon: strip user facts,
  abstract environment services into a capability contract, parameterize invocation
  context, keep method) and is a valid stopping point; stage 2 mechanically applies an
  `adapters/<platform>.md` profile to the generic. Mirrors the workspace-scale
  `harness-generalizer` → `onboarding-adapter` pair at single-skill scale.
- **§4.2 directory convention** (adapters = platform profiles; ports = generated
  deliverables) and the **bundled-file manifest requirement** — every port names the fate
  of every bundled file (attach-as-resource / inline / convert / drop-with-reason),
  including bundled helper skills.
- `adapters/glean.md` — sixth platform profile (Glean Agent Builder), verified against
  docs.glean.com via the Glean MCP server; Glean docs registered as watchlist row 21 in
  the refresher's `source-watchlist.md`.
- Description: Port mode phrasing updated; new trigger phrase "make this skill generic".

---

## [1.7.0] — 2026-07-04

### Changed
- Trimmed SKILL.md per its own context-budget rules; moved duplicated
  tables/details to existing references; pruned citation density (SOURCES.md
  remains the full index).

---

## [1.6.0] — 2026-06-29

### Changed
- `references/audit-rubric.md` §5 Dimension 4 (Evaluation Design) — added a **deterministic /
  script-core carve-out** alongside the 1.5.0 subjective carve-out. Skills whose core *is* a
  tested program (renderer, parser, formatter, validator — e.g. `tool-resume-render`) get their
  functional guarantee from the script's own tests + Level-1 `validate.sh`, not from an LLM
  `eval-cases.md` assertion suite, and must NOT be scored down on this dimension for shipping no
  LLM assertions. Re-anchors the 5/3/1 levels around triggering optimization + a runnable program
  verification. A skill that mixes a deterministic core with real LLM judgment is graded on both
  axes. Triggering/description optimization stays objective and required of every skill.
- `agents/grader.md` — now applies the deterministic/script-core carve-out so a script-wrapping
  skill is not graded down on Evaluation Design for having no LLM assertion suite.
- `scripts/eval.sh` — added `--deterministic`, mirroring `--subjective`: relaxes the functional
  `eval-cases.md` requirement for script-core skills (verify via the bundled script tests +
  Level 1 instead); triggering eval still required. The two flags are mutually exclusive.
- `templates/skill-md-skeleton.md`, `README.md` — documented the third eval category
  (objective / subjective / deterministic) and the new flag.

### Motivation
- The meta-skill was used in Design mode to build `tool-resume-render` (a Python renderer
  wrapped as a skill). Its real eval is "the script produces a valid PDF with the right page
  count" — a script test, not an LLM judgment call. The framework had carve-outs for objective
  and subjective skills but no explicit path for deterministic/script-core skills, risking a
  spurious Dimension-4 downgrade. This closes that gap by mirroring the established 1.5.0 pattern
  (carve-out lives in the rubric + grader + eval.sh + skeleton; SKILL.md body unchanged, stays at
  the 500-line cap).

---

## [1.5.0] — 2026-06-24

### Changed
- `references/audit-rubric.md` §5 Dimension 4 (Evaluation Design) — added a **subjective-skill
  carve-out**: skills whose output is inherently subjective (writing voice/style, tone,
  design, art) are scored qualitatively and are NOT penalized for lacking bundled binary
  assertions or a capability/regression suite. Re-anchors the 5/3/1 levels for such skills
  around triggering optimization + a documented qualitative method (named scorecard + human
  review loop). Triggering/description optimization stays objective and required of every
  skill. Mirrors Anthropic's official `skill-creator` guidance that subjective skills are
  "better evaluated qualitatively — don't force assertions onto things that need human judgment."
- `agents/grader.md` — now applies the subjective-skill carve-out so a voice/writing skill is
  not graded down on Evaluation Design for having no assertion suite.
- `scripts/eval.sh` — eval artifacts and run outputs now live in a **sibling
  `<skill-name>-workspace/`**, never inside the target skill (matches the official
  skill-creator, which treats the skill as input and writes results to a sibling workspace).
  Added `--subjective` to relax the functional-assertion requirement for judgment-based skills;
  triggering eval still required. `--init` now scaffolds the workspace, not the skill.
- `templates/skill-md-skeleton.md` — the `## Evaluation` note + Definition of Done now describe
  on-demand external evaluation into a sibling workspace and the objective-vs-subjective split.

### Motivation
- Verified against Anthropic's installed `skill-creator`: it keeps run results in a sibling
  `<skill>-workspace/` and explicitly evaluates subjective skills qualitatively. Aligning the
  meta-tool prevents a writing/voice skill (e.g. `author-voice`) from being wrongly dinged for
  shipping no eval suite, and keeps target skills clean of eval scaffolding.

---

## [1.4.0] — 2026-06-24

### Added
- `agents/grader.md`, `agents/comparator.md`, `agents/analyzer.md` — the three
  subagent prompt files that §3.1's five-role architecture table already referenced
  but that did not exist in the package. The Grader applies the four-discipline
  rubric in a separate context and emits the §10 Enhancement Handoff Block; the
  Comparator runs a blind A/B between two skill versions to defeat positional bias;
  the Analyzer explains why the winner won. Separating these roles enforces
  generator-assessor separation [generator-assessor-separation-in-skill-iteration]
  and removes the need to hand-roll a grader prompt each time.
- `scripts/eval.sh` — eval readiness gate and scaffolder. Runs `validate.sh` (Level 1),
  checks the skill ships its own `eval-query-set.md` + `references/eval-cases.md`
  (`--init` scaffolds both from templates), prints the Definition of Done checklist,
  and prints the ready-to-paste Grader invocation pointing at `agents/grader.md` and
  `references/audit-rubric.md`. Deterministic plumbing only; it does not grade content.

### Changed
- `templates/skill-md-skeleton.md` — added an `## Evaluation` stub section so every new
  skill is born eval-ready (links `eval-query-set.md` + `references/eval-cases.md`), and
  replaced the pre-publish checklist with a Definition of Done that gates on eval scaffolding,
  the `eval.sh` readiness gate, and a SEPARATE-context grader run via `agents/grader.md`.
- `README.md` — "What's Inside" now lists the `agents/` subagent prompts and `scripts/eval.sh`.

### Motivation
- A new skill was authored, then graded with an improvised rubric, then had to be re-graded
  by-the-book against `audit-rubric.md` (which caught threshold failures the improvised pass
  missed). These additions make the canonical grader and the eval scaffolding turnkey so the
  Eval/Improve loop is a single pass: scaffold evals up front, gate with `eval.sh`, grade in a
  separate context with `agents/grader.md`.

---


### Added
- `WORKFLOW.md` — high-level lifecycle documentation. A Mermaid diagram (with an
  ASCII fallback for non-rendering viewers) maps the four modes (Design, Eval,
  Improve, Port) as entry points that hand off to one another, with the §0.5
  pre-flight primitive gate up front and the §5 security / §6 distribution layers
  wrapping every mode. Documents the two-skill family (`meta-skill-author` +
  `helper-meta-skill-author`) and their differing cadence/actor/mutation profiles.
- `WORKFLOW.md` "When to split this into a routine" section — explicit, finding-cited
  decision criteria for keeping the four modes in one skill versus splitting them
  into a routine of separate skills, grounded in the "structure for scale" guideline
  [skill-authoring-four-guidelines]. Captures the keep-one-skill invariants and the
  triggers (mode outgrows the 500-line cap, a mode develops a different cadence/actor,
  modes stop sharing the spine, or a harness cannot route internal modes) so the
  monolith-vs-routine decision is recorded rather than re-litigated.

### Changed
- `SKILL.md` §0 — the four-modes signpost now points to `WORKFLOW.md` for the
  hand-off map (net-zero edit; SKILL.md stays at the 500-line cap).
- `README.md` — added a Quick Start pointer to `WORKFLOW.md` and a What's Inside row.

---

## [1.2.0] — 2026-06-24

### Added
- `references/skill-smells.md` — a fast symptom-to-cause triage guide. Five smell
  categories (Triggering, Sizing/attention, Authoring-craft, Evaluation/governance,
  Safety/side-effect) map an observable surface symptom to a root cause and the
  reference that diagnoses it. Positioned as the 30-second pre-check before the full
  `references/anti-patterns.md` catalog and `references/audit-rubric.md` audit; does
  not re-prove the anti-patterns. Includes a flagged-smell-count verdict table.
- `references/git-integration.md` — versioning, CI, and distribution guide. Covers the
  skill-as-versioned-policy model [prompt-as-policy-version-control-and-cicd-for-agen],
  repo layout and monorepo context-distribution strategies
  [monorepo-context-distribution-three-strategies], semantic-versioning bump rules,
  a copy-paste CI step that runs `scripts/validate.sh` and fails the build on a
  non-zero exit [bmad-deterministic-skill-validator], branch/review discipline
  (one logical change per PR, sandbox-first, blind behavioral review), and a
  distribution matrix by audience (single repo / org plugin-marketplace / cross-platform
  installer templates / register-and-run) [skill-plugin-marketplace-distribution][multi-ide-portability-via-installer-templates][cross-project-workflow-portability-register-and-run].
- `GETTING-STARTED.md` — a 30-minute on-ramp from "a task I keep doing with AI" to a
  validated, triggering first-skill draft. Five timed steps (pick one real task →
  tacit elicitation → draft from the skeleton → structural validate → trigger gate),
  each with a budget and a single end-of-step artifact. Opens with the §0.5
  is-this-a-skill check and ends with a "next, to reach stable" handoff table.

### Changed
- README Quick Start: added a brand-new-user entry pointing to `GETTING-STARTED.md`
  and a failing-skill entry pointing to `references/skill-smells.md`; renumbered.
- README "What's Inside": added rows for the three new docs.
- SKILL.md: net-zero in-place pointers added — §0.5 → `GETTING-STARTED.md`,
  §2.5 → `references/skill-smells.md`, §6 → `references/git-integration.md`.
  SKILL.md held at the 500-line cap; no rule meaning altered.

### Validation
- `scripts/validate.sh .` → exit 0; SKILL.md = 500 lines (≤ 500). All finding
  citations in the three new docs resolve to existing corpus findings already cited
  elsewhere in the package (three are corpus findings not listed in the SOURCES.md
  multiply-cited table, which by design lists only sources cited by 2+ findings).

---

## [1.1.1] — 2026-06-24

### Added
- SKILL.md §0.5 **"Is a skill the right primitive?"** — a pre-authoring decision
  pointer that rules out cheaper primitives before committing to a skill. Five-row
  table maps the situation to the correct primitive: plain prompt
  [skill-as-new-employee-mental-model], script / code tool
  [code-as-deterministic-tool-inside-skills][skill-vs-process-distinction-deterministic-rails],
  agent / subagent, MCP tool [skills-mcp-recipes-kitchen-complementarity], and
  framework-native [framework-abstraction-tax-for-agents]. Closes the gap where the
  decision-sequence reference assumed a skill was already the chosen primitive.
- SKILL.md §2.2 **"Binary by default — graded only when binary collapses signal"**
  note — makes the binary-vs-graded eval stance explicit: decompose fuzzy goals into
  binary sub-assertions, reserve graded / rubric / LLM-as-judge scoring for genuinely
  subjective dimensions (tone, style, relative quality), and run any judge in a
  separate Grader context [verification-agent-seven-prompt-patterns][generator-assessor-separation-in-skill-iteration].

### Changed
- Tightened §0 orientation prose and the trailing citation block to keep SKILL.md at
  the 500-line cap after the two additions. No rule meaning altered; no citations removed.

### Validation
- `scripts/validate.sh .` → exit 0, 0 errors, 3 advisory warnings (unchanged set);
  SKILL.md = 500 lines (≤ 500). All 7 newly-referenced findings resolve in `SOURCES.md`.

---

## [1.1.0] — 2026-06-24

### Added
- `examples/` — three worked, end-to-end walkthroughs (one per mode):
  - `design-walkthrough.md` — single-task-first → tacit elicitation → spec gate →
    SKILL.md draft → capability eval → ship.
  - `eval-walkthrough.md` — audit a deliberately weak skill across the
    four-discipline rubric in dependency order; produce the enhancement handoff block.
  - `port-walkthrough.md` — one canonical skill → five platform adapters from the
    portable layer + thin wrappers.
- `templates/` — copy-paste starters:
  - `skill-md-skeleton.md` — frontmatter + body scaffold with embedded
    per-section elicitation comments `[yaml-templates-with-embedded-elicitation-instructions]`.
  - `eval-query-set.md` — 20-query description optimization template (8–10 should-
    trigger + 8–10 should-not-trigger, 60/40 split, ≤5 iterations, select by TEST
    score) `[skill-description-optimization-loop-held-out-test]`.
  - `change-manifest.md` — refresher Detect-mode manifest starter.
  - `proposal-log.md` — refresher Propose-mode proposal-log starter.
- `scripts/validate.sh` — portable bash implementation of the Level 1 deterministic
  validator described in `references/audit-rubric.md` §9. Implements the BMAD-style
  19-rule / 6-category model `[bmad-deterministic-skill-validator]`; zero inference
  cost; no network. Exit 0 = PASS (warnings allowed), 1 = FAIL, 2 = usage error.
- `CHANGELOG.md` — this file.

### Changed
- `README.md` — "What's Inside" extended with the `examples/`, `templates/`,
  `scripts/`, and `CHANGELOG.md` entries; Quick Start now points to
  `scripts/validate.sh` for Level 1 validation and `examples/` as the learn-by-doing entry.
- `SKILL.md` §2.5 and §6 — validation references now point to `scripts/validate.sh`
  alongside the conceptual `skills-ref validate` CLI.

### Notes
- These additions form the "ship something today" practitioner tier: spec and
  reference docs were already complete; what was missing was demonstration
  (examples), starters (templates), an executable gate (validator), and a public
  version surface (this changelog).
- All four additions carry the same constraints as the rest of the package:
  finding-cited claims only, portable across all five target platforms, and zero
  Perplexity-only tool references in the refresher-facing material.

## [1.0.0] — 2026-06-23

### Added
- Initial package, rebuilt from 219 directly-relevant research findings (of 764)
  via parallel extraction and per-section rewrite, replacing earlier
  incorrectly-imported design-doc material.
- Core meta-skill `SKILL.md` (4 modes: Design, Eval, Improve, Port) with seven
  sections (Orientation → Design → Eval → Improve → Port → Security/HITL →
  Distribution → Quick Reference).
- `references/` — `superset-spec.md`, `platform-matrix.md`, `decision-sequence.md`,
  `safety-gates.md`, `anti-patterns.md`, `audit-rubric.md`.
- `adapters/` — `claude.md`, `cursor.md`, `copilot.md`, `codex.md`, `perplexity.md`.
- `SOURCES.md` — finding → upstream source map with multiply-cited source table.
- `README.md` — package overview, modes, foundational findings, citation conventions.
- Sibling helper skill `helper-meta-skill-author/` (Detect / Propose / Apply modes)
  with `change-manifest-format.md`, `refresh-validation-pipeline.md`, and
  `source-watchlist.md`. Portable across all five platforms; zero Perplexity-only
  tool references.

### Removed (not confirmed by findings)
- Fractal pattern, librarian internals, and the §Composition/§Construction split
  that had been incorrectly imported from unrelated design-doc material.

[1.1.0]: #110--2026-06-24
[1.0.0]: #100--2026-06-23
