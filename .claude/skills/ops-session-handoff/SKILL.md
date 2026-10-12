---
name: ops-session-handoff
description: >-
  Reconcile a project's PROGRESS document at session end so a fresh session — or a
  teammate with zero prior context — can read that one document and continue. Use when
  ending a session, splitting a long conversation, checkpointing progress, or handing
  off — trigger phrases: "session handoff", "update progress", "wrap up the session",
  "reconcile progress", "hand this off", "end-of-session". Runs a lightweight PM model —
  Vision → Milestone (shippable unit of value) → Scope: PROGRESS is the forward control
  surface (North Star, roadmap, scopes on a Shape-Up hill, next unit of work); HISTORY is
  a Keep-a-Changelog of shipped milestones. Never creates per-session dated handoff files.
license: MIT
metadata:
  port-stage: "generic — stage-1 harness- and workspace-neutral canon (meta-skill-author §4.0)"
  source-skill: "ops-session-handoff v0.16.0"
  re-derive-when: "the source SKILL.md changes; the source is canonical, this file is derived"
  version: "1.0"
---

# Generic port — Session Handoff / Progress Reconciler

> Stage-1 Port deliverable (`meta-skill-author` §4.0). Harness- and workspace-neutral
> canon of `ops-session-handoff`. **Separability bar:** zero user-, workspace-, or
> platform-specific content — this file must pass a separability audit standalone.
> Stage-2 appliers map the **capability contract** below onto one platform via that
> platform's `adapters/<platform>.md` profile; every contract row maps to a platform
> feature or is dropped-with-reason in the stage-2 manifest.

## Goal

The session handoff **is** the project's PROGRESS document — the "session bridge." A
fresh session must read that one document and correctly state the project's purpose,
current status, and the single next action, with **no prior context**. This skill
reconciles a lightweight project-management system across artifacts sharing one spine —
**Vision → Milestone → Scope**:

- **PROGRESS** — the forward control surface: North Star, milestone roadmap, the current
  milestone's scopes on a Shape-Up hill (uphill = figuring out, downhill = executing),
  and the next unit of work.
- **HISTORY** — a Keep-a-Changelog of shipped milestones (newest-first, dated).
- **Atomic change log** (where the host supplies one, e.g. version control) — links the
  two at the individual-change level.

Handoff is the only durable memory a session leaves behind: a session that ends without
reconciling here is simply lost. The skill rewrites PROGRESS in place and files completed
work into HISTORY — it never appends per-session dated handoff files.

## Invocation inputs (host-provided parameters)

Declared at invocation by the host environment — never assumed:

| Input | What the host supplies |
|---|---|
| **Project identity** | Which project's PROGRESS/HISTORY pair to reconcile |
| **Document locations** | Where the PROGRESS and HISTORY documents live (paths, titles, or attached resources) |
| **Track set** | Single-track (one PROGRESS/HISTORY pair) or multi-track (e.g. a system track plus a per-person execution track, each with its own pair). Multi-track adds the routing rule below |
| **Settled-facts ledger** *(optional)* | The canonical store of confirmed facts/retractions about the project's principal subject, if the project keeps one |
| **Do-not-reintroduce list** *(optional)* | Retracted phrases/figures the ledger says must not reappear in project artifacts |

## Capability contract (what any host must supply)

Derived from the skill's `capability-contract.yaml` (canonical, machine-readable —
meta-skill-author §4.0); all rows are optional-tier with the degradations below (the
two deterministic-audit rows share the `script-execution` capability ID).

| Capability | Contract | Degradation if absent |
|---|---|---|
| **Durable editable documents** | Two persistent documents per track (PROGRESS, HISTORY) the agent can read and rewrite in place | Agent outputs the full updated text of each document for the human to paste; never claims to have saved anything it didn't |
| **Versioned checkpoints** | An atomic change log with revert (e.g. git): commits at logical checkpoints make document overwrites reversible | Overwriting PROGRESS drops from Full autonomy to **Proposal-first**; the commit-convention section below is skipped |
| **Change detection** | A way to list what changed this session (e.g. `git status` / diff), read-only | Infer changes from the conversation and the documents' `Updated:` dates; ask the human to confirm the change set |
| **Deterministic ledger audit** | A scriptable read-only scan of project artifacts for do-not-reintroduce phrases sourced from the settled-facts ledger, reporting FAIL/WARN with locations, making no edits | Agent performs the scan manually as a constraint check and flags it as non-deterministic; human spot-checks |
| **Document-hygiene audits** | Deterministic checks on the reconciled docs (e.g. purity: no per-person facts in a shared track; line budget: warn/fail past caps) | Agent applies the same rules manually during reconcile and states in the summary that no deterministic backstop ran |
| **Byproduct store with lifecycles** | A designated place for ephemeral outputs and private generated host-state mirrors, with explicit retention rules | Skip the byproduct sweep and generated-memory mirror; warn that tool outputs may accumulate and generated recall will not travel |
| **Transcript archive** | A host adapter can copy new-or-grown raw session transcripts, including host-archived sessions where exposed, into a durable private store; optional host indexes may report coverage gaps but never replace raw evidence; explicit lineage metadata may classify relationships, but unknowns stay unclassified and queued; a reader normalizes transcripts for recovery/mining | Skip the sync; persist-at-approval discipline becomes the only safeguard for chat-approved decisions |

## Method

### PROGRESS document structure (the forward control surface)

Sections, in order:

1. `Updated: <date>` — bump on every reconcile, with a ≤3-line session summary.
2. **Start here** — a self-bootstrapping pointer: what to load first, then jump to
   Current milestone. Point to HISTORY for shipped work.
3. **North Star** — the durable vision; rarely changes.
4. **Roadmap** — ordered milestones toward the North Star, each a one-line
   definition-of-done, marked `[x] shipped` / `[>] current` / `[ ] planned`.
5. **Current milestone** — the active unit of value:
   - **Definition of done** — what "shipped" means, testable.
   - **Scopes (hill status)** — each work item as `<slug> — <name> — <hill>` where hill ∈
     {uphill, cresting, downhill, done}, plus a one-line note or open unknown. Scopes may
     be discovered mid-milestone.
   - **Next unit of work** — the single scope/action to push next.
6. **Standing items** *(optional)* — durable operational loops and human-only queue items
   belonging to no milestone; pointer-thin lines, detail in each item's canonical home.
7. **Backlog / Icebox** — unscheduled ideas; a holding pen, not the active priority.
8. **Blockers / risks** — stuck scopes (a hill dot that isn't moving is a raised hand).
9. **Decisions & findings** *(optional)* — at most a thin index of standing rules, each
   pointing to its canonical home. PROGRESS is never the decision archive.

**Route-then-compact (critical-path test).** PROGRESS is on the cold-start critical
path: every line is paid at every session start. At each handoff ask — *does a fresh
agent need this line to state the North Star, the current milestone, the next unit of
work, or blockers?* — and route what fails it: shipped-milestone prose → HISTORY (the
roadmap keeps a one-liner); decisions → their canonical home; per-person execution items
→ their track; improvement observations → the project's improvement store if one exists.

### HISTORY document structure (changelog of shipped milestones)

- Newest-first; one section per milestone: `## [M<n> — <name>] — YYYY-MM-DD` (in-progress
  milestones appear as `— Unreleased`; include the change-log range, e.g. commit range,
  when the host has one).
- Under each: a one-line **Outcome** (the value delivered), then completed scopes as
  bullets carrying the rationale — the *why* the atomic log doesn't carry, never a
  file-by-file diff.
- Durable facts, decisions, and guardrails do **not** live here — they live in their
  canonical document; HISTORY may mention where they landed.
- An optional **Descoped** section (above the releases) records backlog items that left
  the control surface *without shipping*: one-liners, newest-first, each opening with a
  disposition label — enum: `out-of-scope` · `superseded` · `wont-do` — plus one line of
  rationale and a date. Deleting a backlog item without a record makes the idea
  unfindable.
- Pre-versioning milestones (no atomic log to reconstruct them) are kept fuller.

### Multi-track routing rule (only when the track set declares multiple tracks)

Litmus test: *would this line still be true and relevant if the tracked person/subject
were swapped for another?* Yes → shared/system track; no → that subject's track. A
capability shipped *by way of* a subject's artifact gets one line in each track — neither
restating the other. Settled facts/retractions about the subject go to the settled-facts
ledger (proposal-first), never to PROGRESS. Shared-track documents stay free of
subject-specific content (path/ID pointers only).

### Commit conventions (only with the versioned-checkpoints capability)

Conventional Commits: `type(scope): imperative summary` + optional rationale bullets +
a `Refs: <scope-slug>` footer threading the commit to its PROGRESS scope. One logical
change per commit; separate content, governance, and tooling changes; a pure
PROGRESS/HISTORY reconcile is its own `docs(pm): …` commit. Prefer 1–3 focused commits
per session.

## Workflow

1. **Collect (infer; don't ask what you can derive).** Via the change-detection
   capability plus the conversation: what was completed, decided, found, and newly opened
   this session. Organize as resolved / unresolved / deferred.
2. **Interview (2–4 targeted questions, only what you can't infer).** The next-session
   goal (offer options drawn from unresolved items), scope boundaries for the next
   session, and — only if they exist — which open thread to prioritize, and whether open
   design decisions are pre-decided or left to the next session.
3. **Reconcile.** Rewrite PROGRESS in place: advance/mark scopes on the hill, add
   discovered scopes, update Roadmap/Backlog/Blockers so nothing contradicts, set the
   next unit of work, bump `Updated:`. File completed scopes into HISTORY under the
   current milestone. If the definition-of-done is met, **ship it**: finalize the HISTORY
   section with the date (+ change-log range if available), mark the Roadmap `[x]`, make
   the next milestone current. Multi-track: repeat per track, routing each outcome per
   the routing rule. Sweep the byproduct store if the host has one.
4. **Reconcile the settled-facts ledger (high-signal gate → human approval)** — only when
   the ledger input was provided. High signal only: an explicit confirmation/correction,
   a retraction of a recorded claim, or a new durable fact — never draft churn or
   unconfirmed hypotheses. Present a draft in the ledger's entry shape; **write only on
   explicit approval**. Optionally run the deterministic ledger audit and surface
   reintroductions for the human to fix — never auto-edit. If signal is low, skip
   silently and note "no ledger changes."
5. **Deliver.** Apply the writes (per the durable-documents capability and its
   degradation), report a 1–3 sentence summary, accept follow-up edits.
6. **Sync continuity archives** (host capabilities only): idempotently copy new-or-grown
   host transcripts into the private workspace archive and mirror generated host memory
   where exposed. Re-run at the next session start to catch the finalized transcript
   tail and asynchronously generated memory. Derive transcript lineage only from explicit
   compatible host metadata; never infer it from timestamps or paths. Unsupported or
   incomplete relationships stay unclassified in the normal review queue. Never rewrite
   a host's native generated memory from the mirror or auto-delete retained mirror files.
7. **Checkpoint** (versioned-checkpoints capability only): commit per the conventions
   above. Local/reversible checkpoints are full-autonomy; anything with lasting external
   effect (push, remote, deploy, delete) is human-required.

## Constraints (and why)

- **No volatile metrics** — never record word/line/file counts or similar; they go stale
  on the next edit. State the durable rule instead.
- **No fake precision** — status is the hill, never percentages or task counts; counts
  hide uncertainty, the hill shows unknown-vs-known.
- **No contradictions** — Roadmap, Current milestone, Backlog, and Blockers must agree;
  contradiction is the single biggest cold-start failure.
- **No context dumping** — reference documents by name/path; never paste their contents
  into PROGRESS. Point at the source of any figure rather than copying data that drifts.
- **Compress, don't accrete** — remove the deliberation behind locked decisions; keep
  durable findings. Every PROGRESS line is paid by every future reader.
- **PROGRESS is forward-only** — completed work lives in HISTORY; never append dated
  session logs.
- **Specify goals + constraints, not every step.**

## Stop rules — halt and ask, never resolve silently

- Nothing meaningful changed → say so and skip; don't manufacture a handoff.
- A session outcome can't be routed unambiguously under the multi-track routing rule →
  ask which track owns it.
- Two live "next" threads compete, or the documents contradict each other → the priority
  is the human's call.
- A milestone's definition-of-done is not verifiably met → do not declare it shipped;
  record what remains.
- A settled-facts-ledger write lacks explicit in-turn approval → the draft waits.
- A hygiene audit would fail on the reconciled documents → fix or surface before
  finalizing.
- The documents can't be found and the human hasn't confirmed their identity → ask;
  never reconcile against a guessed document.
- The human says stop → leave PROGRESS in its last consistent state and report where
  things stand.

## Reversibility & HITL tiers

| Action | Reversibility | Tier |
|---|---|---|
| Collecting context, drafting the reconcile | Fully reversible | Full autonomy |
| Overwriting PROGRESS/HISTORY | Reversible **with** versioned checkpoints | Full autonomy (report a short summary); without checkpoints → Proposal-first |
| Local checkpoint/commit | Reversible | Full autonomy |
| Writing the settled-facts ledger | Governance-grade, high blast radius | Human-required (draft first) |
| Push / remote / deploy / delete | Lasting external effect | Human-required |

## Bundled-file manifest (fate of every file in the source skill)

| Source file | Platform-neutral fate |
|---|---|
| `SKILL.md` | Distilled into this generic; the source remains canonical — re-derive on change |
| `evals/eval-cases.yaml` | **Ships with every port** — the structured eval set (schema: meta-skill-eval references); each port distills the trigger-tier cases into its install-acceptance set (queries + expected verdicts, generic by construction), self-administered post-install. Execution-tier cases run as a program where the host has the `meta-skill-eval` harness |
| `scripts/audit_ledger.py` | Abstracted into the **deterministic ledger audit** contract row. Hosts with script execution port the script (it reads do-not-reintroduce phrases from the ledger, never hard-coded); hosts without degrade per the contract. The workspace-specific artifact paths inside it are stage-2 parameters |
| `scripts/memory_drift.py` | Abstracted into the session-end customization-drift check; mirror parity applies only to active hosts, while machine-only content remains loss-detection evidence. Hosts without inspectable memory/customization scopes drop it with reason |
| `scripts/session_start_sync.py` | Adapter-owned lifecycle wrapper: hosts with a session-start event bind it to the sync scripts; hosts without one retain the next-invocation fallback or drop it with reason |
| `scripts/sync_memories.py` | Abstracted into the **script-execution + byproduct-store** rows. Hosts with inspectable generated memory install a one-way adapter; hosts without it drop the script with reason |
| `scripts/sync_sessions.py`, `scripts/test_sync_sessions.py`, `scripts/transcript.py` | Abstracted into the **transcript archive** contract row. Stage-2 ports install host-specific discovery/parsing, explicit-metadata lineage when available, and deterministic adapter tests; unsupported lineage stays unclassified, or all three files are dropped with reason when the host exposes no local session store |
| `README.md`, `CHANGELOG.md`, `SOURCES.md`, `capability-contract.yaml`, `ports/` | Stay with the source package as audit, provenance, capability, and derived-port machinery |
