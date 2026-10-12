# Decision Sequence: Skill Authoring and Audit Procedure

**Purpose:** Step-by-step authoring and audit procedure for cross-AI skills. Two canonical paths are documented; Path A (iterate-on-single-task) is the Anthropic-endorsed default. Both paths converge on a HARD GATE before proceeding to deployment.

---

## 1. Two Authoring Paths

### Path A — Preferred (Anthropic-endorsed)

**Iterate-on-single-task → distill into SKILL.md → expand to coverage** [iterate-on-single-task-then-extract-skill]

> "Anthropic's primary endorsed methodology: work through ONE challenging task until success, distill the approach into SKILL.md, then expand to coverage testing." [iterate-on-single-task-then-extract-skill]

This path inverts spec-driven development in the critical way: authors systematically guess wrong upfront. Distilling from a task that already worked is empirically more reliable than specifying in advance. [iterate-on-single-task-then-extract-skill]

**Use Path A when:**
- The skill codifies a workflow you have already done successfully with AI
- You cannot fully articulate the tacit knowledge required upfront
- The scope is not yet well-defined

### Path B — Spec-First

**Spec-first → eval design → draft → grade → iterate** [skill-authoring-four-guidelines][spec-first-agent-briefs-prompt-craft-context-inten]

**Use Path B when:**
- The skill's scope is well-defined and has explicit success criteria
- Stakeholders must approve the spec before work begins
- Regulatory or compliance requirements make pre-specification mandatory

**When to switch paths:**
- Spec-first fails when authors cannot articulate tacit knowledge → switch to Path A [tacit-knowledge-as-agent-delegation-barrier]
- Single-task fails when the one task is too narrow to generalize → expand coverage with Path B structure

---

## 2. Path A: Single-Task Sequence (use as default)

### Step 1 — Pick one challenging task

Select one task you have done with an AI that required real effort to succeed. The task must be:
- Representative (not a trivial one-liner)
- One where success required iteration, judgment, or tacit knowledge
- Already completed — you are distilling from a real outcome, not hypothesizing

The four canonical Anthropic authoring orientations apply throughout Path A:
1. Start with evaluation — identify specific capability gaps before building
2. Structure for scale — split when SKILL.md becomes unwieldy; keep mutually exclusive paths separate
3. Think from Claude's perspective — monitor real use; watch name and description as triggering controls
4. Iterate with Claude — ask Claude to capture successful approaches and common mistakes during real work
[skill-authoring-four-guidelines]

### Step 2 — Elicit the tacit knowledge

Expertise compresses into automatic judgment that even experts cannot consciously articulate. A 5-layer elicitation workflow (~45 min) is the concrete mechanism to surface it: [tacit-knowledge-as-agent-delegation-barrier]

1. **Operating rhythms** — When does this workflow run? What triggers it?
2. **Recurring decisions** — What judgment calls do you make consistently?
3. **Required inputs** — What information must be present for the task to succeed?
4. **Recurring friction points** — Where does the task break down? What errors recur?
5. **Success criteria** — How do you know the task is done correctly?

> "Expertise 'compiles' from explicit steps into automatic judgment; even structured interviews cannot fully surface this." [tacit-knowledge-as-agent-delegation-barrier]

Use a YAML template with embedded per-section elicitation instructions to prevent a one-shot document dump. Force section-by-section collaborative production rather than guessing at once. [yaml-templates-with-embedded-elicitation-instructions]

Produce a locked spec artifact (CONTEXT.md equivalent) capturing resolved decisions and clarified constraints before drafting SKILL.md. Implementation begins only when both parties have no more questions. [thinking-partner-philosophy][bidirectional-prompting-for-spec-creation]

> "Implicit assumptions injected from training data are the root cause of most cascading bugs in long agentic runs." [bidirectional-prompting-for-spec-creation]

### Step 3 — Draft SKILL.md from that one task

**Frontmatter first:**
- `name`: 1–64 chars, `[a-z0-9-]`, no reserved words, no XML, matches directory [skill-frontmatter-validation-rules]
- `description`: ≤ 1,024 chars, three-part structure (what + when + capabilities), key use case first [skill-description-structure-what-when-capabilities]
- Declare only open-standard fields unless Claude Code-specific features are required; use `compatibility` if non-portable [skills-as-open-portable-standard]
- For side-effect skills (commit, deploy, send): set `disable-model-invocation: true` [skill-invocation-control-side-effect-guard]

**Body format:**
- Interactive skill → outcome-based, declarative: define success criteria, let the agent explore [declarative-goal-driven-agent-prompting]
- Scheduled / unattended skill → SOP format: numbered steps, named data sources, explicit completion signals, inline edge-case handling [hands-off-routine-prompt-precision-pattern]

**Body completeness check (five layers):**
1. Role & Scope
2. Instructions & Constraints (trust-classified retrieved data)
3. Context & Retrieved Data (pointers, not copies)
4. Examples & Edge Cases (including adversarial cases)
5. Output Format & Tool-Calling (reliability engineering, not readability)
[five-layer-agent-prompt-architecture]

**Anti-pattern audit before finishing the draft:**
- No explicit CoT, few-shot examples, decomposition scaffolding (degrades all three frontier reasoning models) [reasoning-model-anti-pattern-prescribed-reasoning]
- No ALL-CAPS MUST/ALWAYS/NEVER without a WHY explanation alongside [skill-authoring-explain-the-why-not-musts]
- No embedded context copies — use relative path references to `references/` [pointers-over-copies-in-context-files]
- Body ≤ 500 lines; critical content in first 5K tokens [skill-as-directory-progressive-disclosure-three-levels]

**Include an L0 abstract (~100 tokens)** as a named section at the top of the body. Progressive-loading harnesses use this as the only content at boot. [progressive-tiered-context-loading-convergence]

**Declare autonomy tiers** for every side-effect action using the 2×2 blast-radius × reversibility matrix: [autonomy-gradient-not-binary-delegation]

| Blast radius | Reversible | Irreversible |
|-------------|-----------|--------------|
| Low | Full Autonomy | Proposal-first |
| High | Guarded | Human-required |

Persistent mutations of governance docs or schemas: Human-required regardless of track record. [advisory-only-for-persistent-mutations]

### Step 4 — Test on 3–5 variants (capability eval)

Run the skill on 3–5 task variants to verify generalization from the source task:
- Include one obvious variant (paraphrase of the source task)
- Include one near-miss (related but different enough to require adaptation)
- Include one edge case (the most likely failure mode from the friction-point elicitation)

Track with capability eval discipline: capability evals start with low pass rates and should improve with iteration. When a capability eval consistently hits near-100%, it graduates to the regression suite. [capability-vs-regression-eval-lifecycle]

> "Saturated capability evals make progress appear artificially slow." [capability-vs-regression-eval-lifecycle]

Perform holdout validation separately: the validation agent receives only the codebase/test suite, NOT the authoring session context. This prevents sycophancy. [holdout-validation-pattern-blind-regression]

> "LLMs are systemically sycophantic in verification when they know what they just built." [holdout-validation-pattern-blind-regression]

### Step 5 — HARD GATE: Description trigger accuracy

**This gate must not be skipped.** A skill whose description does not trigger reliably is dead capability regardless of body quality. [skill-md-frontmatter-as-discovery-trigger-primitive]

**Description optimization loop:**
1. Construct 20 eval queries: 8–10 should-trigger, 8–10 should-not-trigger (near-misses — sharing keywords but needing something different)
2. Make queries realistic and specific (file paths, company names, casual speech) — "Format this data" is BAD [skill-description-optimization-loop-held-out-test]
3. 60/40 train/test split; run each train query 3 times for a reliable trigger rate
4. ≤ 5 iterations; select best description by TEST score (not train score, to prevent overfitting)
5. Harness: `scripts/prep_eval_loop.py --skills-dir <dir> --out-dir <eval-workspace>` (roster + answer key + shuffled blind batches) → Executor subagents answer the batches blind, one `qid -> verdict` line each → `scripts/score_run.py <verdicts-file>…` (majority rule across runs; `--skills` scopes a seam-scoped re-run after roster changes)
[skill-description-optimization-loop-held-out-test]

**Pass criteria:** 90% trigger rate on relevant queries; 0% trigger on clear non-matches; near-miss discrimination holds. [skill-testing-three-tier-trigger-functional-perf]

**If the gate fails:** Revise the description (not the body) and re-run. Do not promote until the TEST score passes.

> "Claude only triggers skills it can't handle alone — simple single-step queries may not trigger a skill even with a perfect description match." [skill-description-optimization-loop-held-out-test]

### Step 6 — Test on adversarial near-misses (should-not-trigger queries)

Test the skill against queries that are semantically adjacent but should NOT trigger:
- Queries sharing all keywords with the skill's domain but requiring a different skill
- Queries a user might type when they want something related but different
- Overlapping descriptions between skills cause systematic mis-routing [agent-description-auto-dispatch-routing]

If the skill fires on near-misses, narrow the description's trigger phrases or add explicit exclusion language. Check for overlapping descriptions across the full skill catalog. [agent-description-auto-dispatch-routing]

### Step 7 — Promote to stable; add regression eval

When Step 5 (trigger accuracy) and Step 6 (near-miss discrimination) both pass:

1. Run `skills-ref validate ./my-skill` for structural validation [skill-frontmatter-validation-rules]
2. Move the capability eval queries (now passing near-100%) into the regression suite [capability-vs-regression-eval-lifecycle]
3. Add the skill to version control alongside the code it governs [project-specific-custom-skills-for-repeated-task]
4. For team environments: add to `skills-lock.json` via `npx skills` [skills-lock-portable-agent-skills]
5. Benchmark: run baseline (without skill) vs. with-skill on message count, failed calls, tokens consumed, clarifying questions [skill-testing-three-tier-trigger-functional-perf]

---

## 3. Path B: Spec-First Sequence

### Step 1 — Write the 8 spec primitives

Before touching SKILL.md, produce a complete spec covering all eight primitives (verbatim): [spec-first-agent-briefs-prompt-craft-context-inten]

> - Objective + why
> - Success metrics (measurable)
> - Authoritative inputs + definitions
> - Deliverables + exact format
> - Acceptance criteria (verifiable)
> - Constraints: must / must-not / preferences + escalate-if
> - Workflow: plan + checkpoints → confirm → execute → verification notes

If the spec exceeds 30K tokens, decompose into sub-plans. [bidirectional-prompting-for-spec-creation]

### Step 2 — Write the 7 intent engineering parts

Check the spec against the seven-part intent structure. Stop Rules and Constraint types (steering vs. hard) are the most commonly omitted. [intent-engineering-framework-seven-part-agent-inten]

1. **Objective** — The problem + why it matters
2. **Desired Outcomes** — Measurable results, 2–4 max
3. **Health Metrics** — What must not degrade; steer but don't block
4. **Strategic Context** — The broader system the agent operates within
5. **Constraints** — Steering (prompt layer) vs. hard (orchestration layer)
6. **Decision Types / Autonomy** — Which decisions the agent may make vs. must escalate
7. **Stop Rules** — Explicit conditions for halting

> "Context without intent is noise." [intent-engineering-framework-seven-part-agent-inten]

### Step 3 — Define capability eval queries BEFORE writing the body

Write 20 eval queries (8–10 should-trigger, 8–10 should-not-trigger) before drafting the skill body. This prevents description drift and forces the author to define what triggering looks like before anchoring to the body's framing. [skill-description-optimization-loop-held-out-test]

Eval query quality check: are the queries realistic and specific? Do should-not-trigger queries share keywords with the domain but genuinely need something else? [skill-description-optimization-loop-held-out-test]

### Step 4 — Draft body around the spec

Using the locked spec from Step 1, draft the SKILL.md body. The spec governs; the body implements.

Apply the same body authoring rules as Path A Step 3:
- Outcome-based for interactive; SOP for scheduled [declarative-goal-driven-agent-prompting][hands-off-routine-prompt-precision-pattern]
- Five-layer completeness check [five-layer-agent-prompt-architecture]
- Reasoning-model anti-pattern audit [reasoning-model-anti-pattern-prescribed-reasoning]
- Negative constraints over positive aspirations [negative-constraints-as-probabilistic-output-collapse]
- ≤ 500 lines; L0 abstract present; pointers not copies [skill-as-directory-progressive-disclosure-three-levels]

### Step 5 — HARD GATE: Four-discipline rubric

Score the skill body in dependency order (evaluating out of order misdiagnoses failures): [four-discipline-prompt-evaluator]

1. **Prompt Craft** — Word-level instruction quality
2. **Context Engineering** — What information the model has access to
3. **Intent Engineering** — System-level design of agent goals and identity
4. **Specification Engineering** — Structured knowledge systems that constrain and guide behavior
[the-four-discipline-prompting-stack-nate-b-jones]

> "Evaluating in dependency order prevents misdiagnosing a context problem as a craft problem, or an intent problem as a spec problem." [four-discipline-prompt-evaluator]

The output includes a handoff block the enhancer can act on directly. [four-discipline-prompt-evaluator]

> "High rubric scores do not guarantee good agent behavior in practice." — Combine rubric scoring with empirical eval cases. [four-discipline-prompt-evaluator]

> "Your Notion workspace IS specification engineering; CLAUDE.md IS intent engineering." [the-four-discipline-prompting-stack-nate-b-jones]

**Minimum thresholds:** All four disciplines must reach satisfactory before proceeding. A failure in any single dimension blocks promotion. Do not trade off a low Prompt Craft score against a high Specification Engineering score.

**Known limit:** The four disciplines are iterative, not sequential: a Specification Engineering change often requires revisiting Prompt Craft decisions. Risk of over-engineering lower layers (obsessing over word choice) while neglecting Intent and Specification. [the-four-discipline-prompting-stack-nate-b-jones]

### Step 6 — Generator-assessor separation: author does NOT grade

Five distinct subagent roles in separate contexts: [generator-assessor-separation-in-skill-iteration]

1. **Generator** — The author who drafted the skill
2. **Executor** — Per-eval subagent that runs each test case
3. **Grader** — Reads `grader.md`; receives assertions (the spec defines what good looks like, not the grader)
4. **Comparator** — Blind A/B between skill versions (defeats positional bias)
5. **Analyzer** — Works in fresh context; separates "which version won" from "why it won"

> "The skill-creator NEVER both generates and assesses the same artifact in the same context." [generator-assessor-separation-in-skill-iteration]

> "Convenience erosion: under deadline pressure, authors skip the grader subagent — the design must make separation the path of least resistance." [generator-assessor-separation-in-skill-iteration]

If context isolation is impractical, FLAG and document the deviation. Never grade inline without documentation.

### Step 7 — Iterate via Improve mode

- Make one logical change at a time; run the eval harness after each change [claude-code-skills-20-four-mode-skill-lifecycle-wi]
- Apply sandbox-first validation: test all proposed modifications in isolation before committing [sandbox-first-modification-validation]
- Maintain a versioned audit log; automatic rollback capability required [sandbox-first-modification-validation]

HyperAgents evidence: 78–92% of proposed modifications maintain or improve performance; forced rollbacks 8–22%; undetected regressions < 1% with proper sandbox-first governance. [sandbox-first-modification-validation]

---

## 4. HARD Gate Definition

Both paths include a HARD GATE before promotion. A HARD GATE means work stops until the gate passes; there is no conditional promotion.

### Path A HARD Gate: Description trigger accuracy

**Failure condition:** The skill fails to trigger on ≥ 10% of clear positive eval queries OR triggers on any near-miss should-not-trigger query.

**Why this is a hard gate:** A skill that does not trigger is dead capability. Undertriggering bias is documented; the description is the only content Claude sees before deciding to load the skill. [skill-md-frontmatter-as-discovery-trigger-primitive]

**Gate action on failure:** Revise description, re-run optimization loop (≤ 5 more iterations), re-test. Do not touch the body. If trigger accuracy fails after 5 iterations, re-examine the tacit knowledge elicitation (Step 2) — the description may reflect the wrong framing of the skill's purpose.

### Path B HARD Gate: Four-discipline rubric

**Failure condition:** Any single discipline scores below the satisfactory threshold.

**Why this is a hard gate:** Sandbox-first validation evidence shows that unvalidated changes have an 8–22% rollback rate. A four-discipline failure is a leading indicator of runtime behavioral failure. [sandbox-first-modification-validation]

**Gate action on failure:** The rubric's handoff block specifies which dimension failed and what to improve. Apply fixes in dependency order; do not fix Specification Engineering before confirming Prompt Craft is solid. [four-discipline-prompt-evaluator]

---

## 5. When To Switch Paths

| Condition | Action |
|-----------|--------|
| Path B spec-first fails: authors cannot articulate tacit knowledge after 2+ attempts | Switch to Path A; use the 5-layer elicitation workflow before returning to spec [tacit-knowledge-as-agent-delegation-barrier] |
| Path A single-task is too narrow: skill covers only 1 task type | Expand to Path B coverage; use Path B Step 3 (20 eval queries) to define the broader trigger set [skill-description-optimization-loop-held-out-test] |
| Path A description gate fails after 5 iterations | Re-run tacit knowledge elicitation; the description may reflect the wrong framing |
| Path B rubric gate fails on Intent Engineering | Check that Stop Rules and both constraint types (steering + hard) are present [intent-engineering-framework-seven-part-agent-inten] |
| Skill grows past 500 lines | Apply Path B "Structure for scale" guideline: split into separate files; keep mutually exclusive paths in separate skills [skill-authoring-four-guidelines] |

---

## 6. Common Detours (anti-patterns from inventory §2.11)

These detours are the most common ways authoring goes wrong. Each is grounded in a specific finding.

**Detour 1: Skipping eval design first**
Writing the skill body before defining the capability eval queries leads to descriptions optimized for the body's framing rather than for actual triggering accuracy. Path B Step 3 requires eval queries BEFORE the body draft. Path A Step 5 catches this at the HARD GATE. [skill-description-optimization-loop-held-out-test]

**Detour 2: Writing the description after the body (and not optimizing it)**
Description drift — where the description no longer reflects what the workflow does — is a documented failure mode. Updating the body without re-running the description optimization loop silently breaks triggering. [description-based-workflow-routing-lazy-dispatch]

**Detour 3: Self-grading**
Authors grading their own artifacts cannot be objective. Generator-assessor separation is the load-bearing governance rule for the improvement loop. Under deadline pressure, the grader subagent is the first thing skipped — precisely when objectivity matters most. [generator-assessor-separation-in-skill-iteration]

**Detour 4: Context-file instruction bloat**
Verbose SKILL.md or CLAUDE.md files with rules irrelevant to most sessions dilute attention on the relevant content. ETH Zurich quantified this as a 14–22% reasoning token overhead and a ~3% success rate reduction from LLM-generated files. [context-file-instruction-bloat-eth-zurich]

**Detour 5: Prescribed reasoning anti-pattern**
Writing explicit CoT, few-shot examples, or decomposition scaffolding into skill bodies degrades all three frontier reasoning models (GPT-5.4, Claude 4.6, Gemini 3.1). This is a breaking change in prompting convention. Audit every body before deployment. [reasoning-model-anti-pattern-prescribed-reasoning]

**Detour 6: Over-production risk**
Easy meta-skill authoring produces many low-value skills, pressuring the 1% context-window skill-listing budget. Each new skill must clear the description trigger HARD GATE before it consumes budget. [meta-skill-for-skill-authorship]

**Detour 7: Specialization theater**
Adopting agent "teams" that mimic human org charts because the structure feels familiar. Correct decomposition criterion is task characteristics, never organizational structure. [specialization-theater-anti-pattern]

**Detour 8: Convenience erosion**
Under deadline pressure, the entire Path B evaluation pipeline collapses to inline self-assessment. The sequence must be designed to make separation the path of least resistance — not an optional extra step. [generator-assessor-separation-in-skill-iteration]

---

*Total: approximately 310 lines. All claims cite a finding from the master inventory. HARD gates are grounded in the sandbox-first validation evidence and description trigger accuracy evidence.*
