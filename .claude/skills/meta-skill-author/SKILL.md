---
name: meta-skill-author
description: >-
  Creates, evaluates, improves, and ports reusable agent capabilities (skills,
  agents, prompt packages) on any AI platform. Use when designing a new
  skill/agent, auditing an existing one, optimizing triggering accuracy,
  evaluating quality across the four disciplines (Prompt Craft, Context
  Engineering, Intent Engineering, Specification Engineering), or packaging a
  capability for multi-platform deployment. Four operating modes: Design
  (create spec-first), Eval (score + optimize), Improve (iterate with
  generator-assessor separation), Port (two-stage: generalize to a
  harness-neutral generic, then adapt to a target platform via its adapter).
  Trigger phrases: "write a skill", "design an agent", "audit this skill",
  "port this skill", "make this generic", "improve this skill", "optimize
  description", "evaluate skill quality".
license: MIT
metadata:
  port-stage: "generic — stage-1 harness- and workspace-neutral canon (meta-skill-author §4.0)"
  source-skill: "meta-skill-author v1.20.0"
  re-derive-when: "the source SKILL.md changes; the source is canonical, this file is derived"
  version: "1.0"
---

# Generic port — Skill Author (meta)

> Stage-1 Port deliverable (`meta-skill-author` §4.0 — this skill's own method applied
> to itself). Harness- and workspace-neutral canon. **Separability bar:** zero user-,
> workspace-, or platform-specific content. On non-file harnesses the authoring target
> shifts from SKILL.md files to that platform's capability unit (agents, prompt
> packages) — the **method** is what ports. Stage-2 appliers map the capability contract
> onto one platform via its adapter profile.

## Goal

A skill is the AI equivalent of an SOP: encode once, invoke reliably. This skill's
product is a well-formed capability definition — name, description, instructions,
permissions — or a scored audit / improvement / port of an existing one. Skill
authorship is **distillation, not specification**: work one challenging representative
task with the model until it succeeds, then encode what bridged the gap. The description
**is** the skill at runtime: a capability that never triggers is dead capability.

## Invocation inputs (host-provided parameters)

| Input | What the host supplies |
|---|---|
| **Authoring target** | The platform's capability unit and its field constraints (e.g. SKILL.md frontmatter caps, agent-builder field limits) |
| **Candidate task** | One concrete, representative, hard case to distill from |
| **Existing artifact** *(Eval/Improve/Port modes)* | The capability definition being scored, improved, or ported |
| **Distribution scope** | Internal (lives in this workspace) or exportable (leaves it) — ask the human; never assume |

## Capability contract (what any host must supply)

Derived from the skill's `capability-contract.yaml` (canonical, machine-readable —
§4.0); the approval channel is **required**-tier (inert without it), and the validator
and eval-harness rows share the `script-execution` capability ID.

| Capability | Contract | Degradation if absent |
|---|---|---|
| **Interactive approval channel** | Present the spec (and later gates) for explicit human approval before generating | None permitted — the spec-first gate is the method; unattended runs require a pre-approved spec |
| **Deterministic structural validation** | A scriptable validator for the platform's capability format, run before any LLM review | Agent checks field constraints manually and states that no deterministic pass ran; never skips the check entirely |
| **Eval harness** | Executable trigger-accuracy evals (train/test split, held-out selection) | Description optimization falls back to heuristic review against the [What]+[When]+[capabilities] pattern; flag that accuracy is unmeasured |
| **Separate assessor context** | A way to run graded judging in a context that is not the author's (subagent, second session, second human) | Grading degrades to self-review — flag it: convenience erosion of generator-assessor separation is the primary known failure mode |
| **Versioned artifact store** | Change history for capability definitions (versioning, rollback) | Carry version + changelog inside the artifact itself; warn that rollback is manual |
| **Reference bundle** | The package's reference documents (rubric, anti-patterns, platform matrix, field spec) attachable at invocation | Inline the condensed versions carried in this body; audits cite the summary, not the full rubric |

## Method

### First gate: is a skill the right primitive?

The most common authoring mistake is building a skill for what should be a plainer
primitive. Rule out cheaper options first: a plain prompt (the base model already
handles it in one shot) · a script/code tool (fully deterministic logic) · an
agent/subagent (persistent identity, long-horizon autonomy) · an external-capability
connector (API/DB exposure). If none fits and the task is reusable expertise that
triggers by description, author a skill.

### Design mode — spec-first, gate-before-generate

1. **Start with one task.** Work one challenging representative task to success;
   distill the winning approach; then expand to coverage.
2. **Elicit tacit knowledge** before drafting — structured batches, never a one-shot
   dump: operating rhythms · recurring decisions · required inputs · recurring friction
   points · success criteria.
3. **Spec-first gate — human approves before any generation.** Eight spec primitives:
   objective+why · success metrics · authoritative inputs · deliverables+format ·
   verifiable acceptance criteria · constraints (must/must-not/escalate-if) ·
   workflow+checkpoints · escalation triggers. Confirm **stop rules** are present (the
   most commonly omitted element). Declare execution mode: interactive (outcome-based)
   or scheduled/unattended (numbered SOP, completion signal). Declare **distribution
   scope**: internal = lean package, may bind to local paths freely; exportable = full
   distribution package with versioning and the separability bar from day one.
   Scaffolding scales with distribution distance, not importance; undeclared scope
   defaults to internal, and later export must run a stage-1 Generalize first.
4. **Description authoring.** [What] + [When] + [Key capabilities], key use case first;
   include trigger phrases; "a little bit pushy" combats undertriggering; respect the
   platform's length cap.
5. **Body authoring.** Outcome-based (declarative) over procedural for interactive
   skills; explain the WHY behind every constraint; behavioral rules as negative
   constraints; pointers over copies; omit anything the model can discover itself.
   Front-load critical content; keep within the platform's size budget. Mandatory
   fields: stop rules · reversibility class per side-effect · HITL tier per action.

### Eval mode — measure, don't guess

- **Description optimization:** build ~20 realistic eval queries (8–10 should-trigger
  paraphrases + 8–10 should-not-trigger near-misses), split train/test, iterate ≤5
  times, select by TEST score (prevents overfitting). The finished set graduates into
  the package as a structured eval file — each query paired with its expected verdict —
  written user-content-free from the first draft (real phrasings seed intent shapes but
  never travel verbatim; use specific-but-fictional equivalents), so a receiving agent
  can self-administer the trigger cases as its install acceptance check.
- **Author output-first.** Optionally classify the set: capability-uplift (improves
  output over a skill-masked baseline; can eventually retire) vs. encoded-preference
  (output faithfully follows the intended workflow). Functional cases grade final
  artifacts first with typed failure categories; where deterministic artifact
  verification is possible, construct a known-good oracle and require it to pass every
  verifier before accepting the case. Keep assertions parsimonious and distinct.
  Trajectory/single-step grading is diagnostic only (failures, surprising passes,
  graduation, model/harness changes) and stops at failure-class saturation; trigger
  success is never a proxy for output quality.
- **Four-discipline rubric**, scored in dependency order — Prompt Craft → Context
  Engineering → Intent Engineering → Specification Engineering — with binary pass/fail
  assertions; graded judging runs in a separate assessor context.
- **Deterministic validation first:** run the structural validator BEFORE any LLM
  review, never instead of it.
- Three test tiers: triggering (positive + negative) · functional · performance vs.
  baseline. Capability evals graduate to regression near 100%. Where the host carries
  an eval-harness program, full-set execution and the graduation/saturation/retirement
  lifecycle read from that harness's attributed ledger, never asserted from memory.

### Improve mode — generator-assessor separation

The author never both generates and assesses the same artifact in the same context.
Roles: Generator · Executor (per eval) · Grader · Comparator · Analyzer — separate
contexts. Modifications go sandbox-first: isolate → significance gate → held-out
re-validation → rollback on regression. Keep a lessons log: after any invocation that
produced correction, token waste, or lost work, append what went wrong · fix · rule;
prune beyond ~10. Critic-verifier loop terminates at an iteration cap or confidence
threshold; the critic fails closed.

### Port mode — two-stage: Generalize → Apply

Stage 1 (**Generalize**) produces `ports/generic.md` in the skill's own directory — the
harness-neutral canon. Classify every binding: user/workspace facts → **strip**;
environment services → **abstract into a capability contract** (named list of what any
host must supply, each with a degradation note); invocation context → **parameterize**
as explicit host-provided inputs; method content → **keep**. Stage 1 is a valid
stopping point.

Stage 2 (**Apply**) produces `ports/<platform>-*.md` — a mechanical mapping of the
generic's contract onto one platform via that platform's `adapters/<platform>.md`
profile (adapter = recipe; generic = base sauce; port = dish). No adapter yet → author
the profile first. Every port carries a **bundled-file manifest** naming the fate of
every file in the source package: attach-as-resource / inline / convert /
drop-with-reason. A platform port existing without a generic (stage fusion under time
pressure) must be backfilled before a second platform — two fused ports diverge; one
generic + two applies don't.

Before porting, audit the body for reasoning-model anti-patterns — explicit
chain-of-thought, few-shot scaffolds, self-consistency, forced decomposition — and
replace with **Goal + Constraints + Context**.

### Security & autonomy

Audit three attack surfaces before publishing: static instructions · bundled scripts ·
dynamic external fetching (trust at the domain level, not the URL). Principle of Lack
of Surprise; permission-grant inflation is a named risk. Autonomy per side-effect via
the 2×2 (blast radius × reversibility): low/reversible = full autonomy ·
low/irreversible = proposal-first · high/reversible = guarded · high/irreversible =
human-required. Hard rule: persistent mutations of governance docs, schemas, or
platform configs are human-required regardless of track record. On always-on harnesses
with weak per-skill permissioning, the guard lives in the body: never commit, push,
deploy, or delete without explicit approval. Truly irreversible actions are never
delegated to skills.

## Constraints (and why)

- **Distillation, not specification** — encode only what bridged a real gap; skills for
  tasks the base model handles alone are dead weight.
- **Gate before generate** — implicit assumptions cause cascading failures in long
  runs; the locked spec is the cheapest failure point.
- **Measure triggering; don't guess** — description quality is testable; select by
  held-out score.
- **Separate generation from assessment** — same-context self-grading erodes silently.
- **Deterministic checks before LLM review, never instead of** — structure is cheap to
  verify; judgment is not.
- **No volatile metrics in durable artifacts** — durable rules only.

## Stop rules — halt and ask, never resolve silently

- The primitive-selection gate says a skill is the wrong tool → say so; do not author.
- The human has not approved the spec → no generation.
- Distribution scope is undeclared → ask; on silence default to internal and say so.
- An eval-measured change regresses the held-out score → roll back, report.
- A port would drop a bundled file without a stated reason → the manifest is incomplete.
- Any action would mutate governance-grade configuration → human-required.

## Reversibility & HITL tiers

| Action | Reversibility | Tier |
|---|---|---|
| Elicitation, spec drafting, audits shown in conversation | Fully reversible | Full autonomy |
| Creating/editing a capability definition in the versioned store | Reversible | Proposal-first at the spec gate, then full autonomy within the approved spec |
| Publishing/sharing a capability beyond the workspace | Practically irreversible | Human-required |
| Modifying this method's own configuration | Governance-grade | Human-required + re-verify previously-passing skills |

## Bundled-file manifest (fate of every file in the source skill)

| Source file(s) | Platform-neutral fate |
|---|---|
| `SKILL.md` | Distilled into this generic; the source remains canonical — re-derive on change |
| `evals/eval-cases.yaml` | **Ships with every port** — the structured eval set (schema: meta-skill-eval references); each port distills the trigger-tier cases into its install-acceptance set (queries + expected verdicts, generic by construction), self-administered post-install. Execution-tier cases run as a program where the host has the `meta-skill-eval` harness |
| `references/audit-rubric.md`, `references/anti-patterns.md`, `references/skill-smells.md`, `references/decision-sequence.md` | Abstracted into the **reference bundle** contract row — method content that generalizes; attach where hosts carry resources, else the inlined summaries above stand in |
| `references/capability-vocabulary.md` | **Ships with every port that authors exportable capabilities** — the controlled ID list capability contracts and adapter Provides inventories are graded against; without it, contracts degrade to free-text capability names flagged as unverifiable |
| `references/superset-spec.md`, `references/platform-matrix.md`, `references/git-integration.md`, `references/safety-gates.md` | **Stage-2 decision per platform** — field/format/git mechanics; attach on file-based harnesses, drop-with-reason elsewhere |
| `scripts/validate.sh`, `scripts/eval.sh` + `scripts/prep_eval_loop.py` + `scripts/score_run.py` (eval harness) | Abstracted into the **deterministic structural validation** and **eval harness** contract rows; port the scripts where execution exists, degrade per contract otherwise |
| `adapters/` (per-platform profiles) | **Stays with the source package** — consumed at authoring time by Port mode; each stage-2 apply reads exactly one |
| `templates/`, `agents/`, `examples/`, `WORKFLOW.md`, `GETTING-STARTED.md`, `SOURCES.md`, `CHANGELOG.md`, `README.md` | **Stays with the source package** — authoring-time scaffolding and provenance for the distribution package; not part of the runtime method |
| `helper-meta-skill-author/` (bundled refresher sub-skill) | **Stays with the source package, by design** — it maintains the local package via sandbox-validated edits and watches upstream sources; hosts get its benefit indirectly through re-derived ports |
