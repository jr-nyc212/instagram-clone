# Audit Rubric Reference

> Reference doc for the cross-AI skill-authoring meta-skill.
> The four-discipline audit rubric verbatim, with scoring procedure, capability/regression eval design,
> description optimization eval design, verification levels, and enhancement handoff format.
> Every claim cites a finding from the master inventory.

---

## 1. The Four Disciplines (Dependency Order) [the-four-discipline-prompting-stack-nate-b-jones]

Nate B. Jones's four-discipline framework organizes all prompting work into four ascending layers. Each discipline depends on and amplifies the layers below it. The framework is the diagnostic spine for all skill auditing: a bad output must be triaged to a specific layer before a fix can be prescribed.

> "Most practitioners conflate all four disciplines into 'prompting,' which obscures where problems actually originate and where improvements will have the most leverage." [the-four-discipline-prompting-stack-nate-b-jones]

### Discipline 1 — Prompt Craft
**Word-level instruction quality.** The clarity, precision, and completeness of individual instructions within the skill body. Problems here are visible in a single read of the text.

### Discipline 2 — Context Engineering
**What information the model has access to.** How context is scoped, curated, and delivered: which files are loaded, what format they are in, how stale or fresh they are. Context engineering failures are invisible in the text but visible in runtime behavior when the model lacks needed information or is flooded with irrelevant noise.

### Discipline 3 — Intent Engineering
**System-level design of agent goals and identity — what CLAUDE.md does.** Encoding what the agent is trying to accomplish, what constraints it must honor, and what authority it holds. Intent engineering failures produce an agent that performs tasks correctly in isolation but makes the wrong judgment when instructions run out.

> "Context without intent is noise." [intent-engineering-framework-seven-part-agent-inten]

### Discipline 4 — Specification Engineering
**Structured knowledge systems that constrain and guide agent behavior — what a well-built Notion workspace does.** The organizational architecture of skills, references, and constraints as a system. Specification engineering failures produce inconsistent or unverifiable behavior that no amount of prompt rewriting fixes.

> Concrete artifact mapping (verbatim): "Your Notion workspace IS specification engineering; CLAUDE.md IS intent engineering." [the-four-discipline-prompting-stack-nate-b-jones]

**Diagnostic principle (verbatim):** "A bad output might be a Prompt Craft failure, a Context failure, an Intent failure, or a Specification failure — each requiring a different fix." [the-four-discipline-prompting-stack-nate-b-jones]

---

## 2. Discipline 1: Prompt Craft Rubric [four-discipline-prompt-evaluator]

Prompt Craft is evaluated as pass/fail across six elements. A skill must pass all six to clear this discipline. Failures here indicate word-level instruction problems that must be fixed before evaluating higher layers.

| Element | Pass condition | Fail condition |
|---------|---------------|----------------|
| **Role** | Agent has a clear, specific role declaration that establishes identity and scope | No role declared, or role is so broad it provides no constraint ("be a helpful assistant") |
| **Task clarity** | The primary task is unambiguous; a third party could describe it without consulting the author | Task requires inference about the author's intent; multiple plausible interpretations exist |
| **Output format** | Format is explicitly specified: structure, fields, length, encoding | Format is implicit or described only as "professional" or "clear" |
| **Constraints** | Constraints specify what must and must not happen, with reasoning | No constraints, or only positive aspirations with no negative prohibitions |
| **Success criteria** | Criteria are verifiable by a third party; binary pass/fail checkable | Criteria are subjective ("output should be good") or absent |
| **Self-check** | Skill includes a verification step or the agent can confirm task completion independently | No self-check; agent declares success without evidence |

**Calibration note:** The self-check element is the most commonly missing. A skill that produces output and stops without verification is treating file creation as completion — the "work disavowal" anti-pattern [mandatory-user-acceptance-testing-uat-at-phase-bo].

**Known limit:** "High rubric scores do not guarantee good agent behavior in practice. A prompt can score well on all four dimensions and still fail at runtime due to model behavior, tool limitations, or context not captured in the prompt itself." [four-discipline-prompt-evaluator] The rubric is a necessary but not sufficient audit; combine with empirical eval cases (§7).

---

## 3. Discipline 2: Context Engineering Rubric [four-discipline-prompt-evaluator]

Context Engineering is scored 1–5 across four dimensions. Score each independently; the lowest dimension score is the bottleneck.

### Dimension 1: Source Scoping
*Is context loaded from the minimum necessary sources with explicit justification for each?*

| Score | Description |
|-------|-------------|
| 5 | Every context source is explicitly declared; sources not needed for this task are excluded; pointers used over copies |
| 4 | Sources declared; minor over-inclusion that does not materially affect performance |
| 3 | Some undeclared or implicit sources; some copies where pointers would suffice |
| 2 | Significant over-inclusion of context not relevant to most invocations; context bloat measurable |
| 1 | All available context loaded indiscriminately; or critical context entirely absent |

ETH Zurich evidence: LLM-generated context files add 14-22% reasoning overhead and reduce success rates ~3% [context-file-instruction-bloat-eth-zurich]. Target Score ≥ 4.

### Dimension 2: Signal-to-Noise
*Does every instruction in context earn its place? Would removing it degrade performance?*

| Score | Description |
|-------|-------------|
| 5 | Each instruction passes the minimum-viable-rule test: the author would type it at the start of nearly every session [claudemd-minimum-viable-rule-only-add-globally] |
| 4 | Mostly necessary; 1-2 instructions that apply only to minority of invocations |
| 3 | ~20-30% of instructions are session-irrelevant noise; attention dilution measurable |
| 2 | Majority of instructions are edge-case-specific; core instructions buried in noise |
| 1 | Context is a dumped document (auto-generated or copy-pasted); no curation evidence |

"A 700-line CLAUDE.md where 650 lines are irrelevant doesn't give Claude more power — it dilutes the 50 relevant lines." [claudemd-as-signal-to-noise-problem-not-size-probl]

### Dimension 3: Dynamic vs. Static Balance
*Is the right content loaded statically vs. injected dynamically?*

| Score | Description |
|-------|-------------|
| 5 | Invariant content is static (frontmatter, body); variable content is dynamically injected at invocation via `!`cmd or tool calls |
| 4 | Mostly appropriate; minor static content that should be dynamic or vice versa |
| 3 | Some invariant content that changes between sessions loaded dynamically (token waste); or some dynamic content hardcoded statically (staleness risk) |
| 2 | Significant misclassification: large dynamic chunks in static body, or stale hardcoded values |
| 1 | No dynamic injection used where clearly needed; or dynamic injection on all content (no stable anchors) |

Dynamic context injection via `!`cmd is resolved once at activation; output is NOT re-scanned for nested placeholders [skill-dynamic-context-injection-shell-prerender].

### Dimension 4: Memory / State Across Sessions
*Is session state handled explicitly, or is it assumed to persist implicitly?*

| Score | Description |
|-------|-------------|
| 5 | Session bridging is explicit: progress, decisions, and state are written to named files; skill writes its own standing instructions (invariants), not one-time setup steps [skill-content-lifecycle-context-budget] |
| 4 | Most state is explicit; minor implicit assumptions |
| 3 | Some state assumed to persist without mechanism; partial session bridging |
| 2 | Significant reliance on implicit context persistence; frequent context-start failures |
| 1 | No state management; skill behaves as if every invocation is the first |

---

## 4. Discipline 3: Intent Engineering Rubric [four-discipline-prompt-evaluator] [intent-engineering-framework-seven-part-agent-inten]

Intent Engineering is scored 1–5 across four dimensions, grounded in the seven-part intent framework.

### The Seven-Part Intent Structure (verbatim) [intent-engineering-framework-seven-part-agent-inten]

Every skill must be evaluated against all seven components. The most commonly omitted components are Stop Rules (component 7) and the two-type constraint distinction (component 5).

1. **Objective** — The problem + why it matters
2. **Desired Outcomes** — Measurable results, 2–4 max
3. **Health Metrics** — What must not degrade; steer but don't block
4. **Strategic Context** — The broader system the agent operates within
5. **Constraints** — Two types: steering (prompt layer) and hard (orchestration layer)
6. **Decision Types / Autonomy** — Which decisions the agent may make vs. must escalate
7. **Stop Rules** — Explicit conditions for halting

> "Intent is what determines how an agent acts when instructions run out." [intent-engineering-framework-seven-part-agent-inten]

### Dimension 1: Goal Explicitness
*Is the objective (component 1) and desired outcomes (component 2) unambiguous?*

| Score | Description |
|-------|-------------|
| 5 | Objective includes both the problem AND why it matters; 2-4 measurable desired outcomes declared |
| 4 | Clear objective; outcomes present but 1 is unmeasurable |
| 3 | Objective present but no stated "why"; outcomes vague |
| 2 | Implicit objective (reader must infer); no outcomes |
| 1 | No objective stated; skill is a capability without a purpose |

### Dimension 2: Constraint Architecture
*Are both constraint types present (component 5) and correctly placed?*

| Score | Description |
|-------|-------------|
| 5 | Steering constraints (prompt layer: behavioral guidance) and hard constraints (orchestration layer: numeric thresholds, enforce-not-just-instruct) are distinct and explicitly labeled |
| 4 | Both types present; labeling could be clearer |
| 3 | Constraints present but not categorized; hard constraints implemented as steering instructions only |
| 2 | Only one constraint type; the two-type distinction is absent |
| 1 | No constraints, or constraints that are purely positive aspirations [negative-constraints-as-probabilistic-output-collapse] |

"The two-type constraint distinction — steering via prompt layer vs. hard enforcement in orchestration — requires architectural separation and is directly actionable." [intent-engineering-framework-seven-part-agent-inten]

### Dimension 3: Klarna Test (Autonomy Boundary Clarity)
*Is it clear exactly which decisions the agent may make autonomously vs. must escalate (component 6)?*

| Score | Description |
|-------|-------------|
| 5 | Per-decision-type autonomy tier assigned (Full / Guarded / Proposal-first / Human-required) [autonomy-gradient-not-binary-delegation]; Klarna test passable: an auditor can determine the agent's authority without asking the author |
| 4 | Most decisions classified; 1-2 edge cases ambiguous |
| 3 | Blanket autonomy level declared (no per-decision granularity) |
| 2 | Implicit autonomy; escalation conditions described but not as decision types |
| 1 | No autonomy specification; agent will make all decisions unilaterally |

### Dimension 4: Autonomy Boundaries and Stop Rules
*Are Stop Rules (component 7) and Health Metrics (component 3) present and specific?*

| Score | Description |
|-------|-------------|
| 5 | Stop Rules: explicit halting conditions (not just failure modes); Health Metrics: quantified ("latency must not exceed 2s"), not qualitative; both components 3 and 7 present |
| 4 | Stop Rules present; Health Metrics present but 1 is not quantified |
| 3 | Either Stop Rules or Health Metrics present, not both |
| 2 | Implicit stop conditions only ("stop when done"); no health metrics |
| 1 | No Stop Rules; no Health Metrics; skill runs until it runs out of context or errors |

Stop Rules are the most commonly omitted intent component. An agent without explicit stop conditions will run until context exhaustion, error, or a human intervenes [intent-engineering-framework-seven-part-agent-inten].

---

## 5. Discipline 4: Specification Engineering Rubric [four-discipline-prompt-evaluator]

Specification Engineering is scored 1–5 across four dimensions. This layer governs the skill as a system artifact, not just its prose content.

### Dimension 1: Self-Containment
*Can the skill be understood and executed without requiring context from its authoring session?*

| Score | Description |
|-------|-------------|
| 5 | Skill is fully self-contained: all dependencies declared, all references use relative paths, no implicit authoring-session context assumed |
| 4 | Mostly self-contained; 1 implicit dependency |
| 3 | Some implicit dependencies (assumes CLAUDE.md conventions, assumes loaded sister skills) |
| 2 | Significant implicit dependencies; fails in a fresh session without the author's mental model |
| 1 | Requires reading the authoring session to understand; not independently executable |

Skills targeting `agent: Explore` (forked execution) must not assume CLAUDE.md conventions are loaded — they are not [skill-forked-subagent-execution].

### Dimension 2: Acceptance Criteria
*Are verifiable acceptance criteria present that a third party could evaluate independently?*

| Score | Description |
|-------|-------------|
| 5 | Verifiable pass/fail acceptance criteria present (e.g., "output contains a summary under 200 words with at least 3 cited sources"); 3-5 known-good eval cases saved as baseline |
| 4 | Criteria present and mostly verifiable; 1 is subjective |
| 3 | Criteria present but none are independently verifiable without consulting the author |
| 2 | No acceptance criteria; success is undefined |
| 1 | Success defined as "output should be good" or equivalent |

"The most reliable way to prevent agent drift and detect output quality issues is to define acceptance criteria that a third party (not the prompter) could verify independently." [acceptance-criteria-as-verifiable-eval-anchor]

### Dimension 3: Task Decomposition
*Is the skill's scope appropriate — neither too broad nor too narrow?*

| Score | Description |
|-------|-------------|
| 5 | Scope is a single coherent capability; mutually exclusive with other skills; split criteria defined (when SKILL.md becomes unwieldy, split into separate skills) [skill-authoring-four-guidelines] |
| 4 | Mostly coherent; minor scope overlap with adjacent skills |
| 3 | Two or more distinct capabilities bundled; should be split but not critically |
| 2 | Significant bundling; skill handles 3+ distinct use cases |
| 1 | Monolithic skill trying to handle all cases; no decomposition |

### Dimension 4: Evaluation Design
*Is the skill equipped with an eval infrastructure that makes quality measurable?*

| Score | Description |
|-------|-------------|
| 5 | Eval suite present with capability/regression split [capability-vs-regression-eval-lifecycle]; description optimization loop completed [skill-description-optimization-loop-held-out-test]; binary pass/fail assertions for acceptance criteria [verification-agent-seven-prompt-patterns] |
| 4 | Eval suite present; one of the three components missing |
| 3 | Basic eval present (some test cases) but no capability/regression split and no description eval |
| 2 | No eval infrastructure; quality assessed only by author judgment |
| 1 | No evals; no acceptance criteria; quality is entirely subjective |

**Subjective-skill carve-out.** Skills whose primary output is inherently subjective —
writing voice/style, tone, design, art — are evaluated **qualitatively**, not with bundled
binary assertions, and must NOT be scored down on this dimension for lacking a functional
eval suite. Forcing pass/fail assertions onto judgment-based output produces brittle,
misleading gates. This mirrors Anthropic's official `skill-creator` guidance: *"Skills with
subjective outputs (writing style, art) often don't need [test cases]… better evaluated
qualitatively — don't force assertions onto things that need human judgment."* For a
subjective skill, re-anchor Dimension 4:

- **5** = the description/triggering optimization is completed AND a documented qualitative
  method exists (a named review rubric/scorecard plus a human-in-the-loop review loop);
- **3** = one of those two is present;
- **1** = neither — no triggering eval and no defined way to judge quality.

The capability/regression split and binary-assertion requirements in the table above apply
only to skills with objectively verifiable output (file transforms, data extraction, code
generation, fixed workflow steps). Triggering/description optimization, by contrast, is
objective and applies to **every** skill regardless of output type.

**Deterministic / script-core carve-out.** Skills whose core *is* a deterministic program —
a renderer, parser, formatter, validator, or other tool that wraps a tested script
(e.g. `tool-resume-render`) — get their functional guarantee from the **script's own tests**,
not from an LLM-graded assertion suite. The determinism lives in code, so the correct eval is
running that code: the bundled tests pass and Level-1 `validate.sh` passes. Do NOT score such a
skill down on this dimension for shipping no LLM `eval-cases.md`; that would be a misdiagnosis
(asking an LLM judge to re-verify behavior a script already verifies deterministically). For a
script-core skill, re-anchor Dimension 4:

- **5** = the description/triggering optimization is completed AND the skill ships a runnable
  verification of its program (its own tests, or a documented golden-output check) that passes
  alongside Level-1 validation;
- **3** = one of those two is present;
- **1** = neither — no triggering eval and no runnable way to verify the program.

A skill that *combines* a deterministic core with genuine LLM judgment (e.g. the script renders
but a model selects content) is evaluated on both axes: script tests for the deterministic part,
binary assertions or qualitative review for the judgment part. Triggering/description
optimization remains objective and required of every skill.

---

## 6. Scoring Procedure [four-discipline-prompt-evaluator]

### 6.1 Score in Dependency Order

Always score in the following order: Prompt Craft → Context Engineering → Intent Engineering → Specification Engineering.

**Rationale:** "Evaluating in dependency order prevents misdiagnosing a context problem as a craft problem, or an intent problem as a spec problem." [four-discipline-prompt-evaluator] A skill that fails Prompt Craft may appear to fail Context Engineering when the actual problem is a word-level instruction ambiguity. Fix in order; do not advance to a higher layer until the lower layer clears.

### 6.2 Calibration Notes

1. **The rubric diagnoses; evals verify.** A skill that passes the rubric on all four dimensions may still fail in production. The rubric identifies which layer to fix; empirical eval cases confirm the fix worked [four-discipline-prompt-evaluator].

2. **Iterative, not sequential authoring.** The four disciplines are evaluated in dependency order, but authoring must cycle. A Specification Engineering change (e.g., reorganizing reference files) often requires revisiting Prompt Craft decisions. "Iterative, not sequential" is the authoring reality; dependency order is the evaluation reality [the-four-discipline-prompting-stack-nate-b-jones].

3. **Domain weighting.** Some contexts weight dimensions differently: coding skills weight Specification Engineering precision more heavily; conversational skills weight Intent Engineering more heavily. Core rubric dimensions do not change, but calibration of what constitutes a "5" varies by domain [four-discipline-prompt-evaluator].

4. **Rubric score ≠ deployment clearance.** A skill may score 5/5/5/5 and still fail due to model behavior changes, tool availability differences, or context not captured in the prompt. Rubric scoring is the authoring-time gate; behavioral verification is the deployment-time gate.

### 6.3 Generator-Assessor Separation: Who Runs the Rubric? [generator-assessor-separation-in-skill-iteration]

The person (or agent context) that authored the skill **must not** run the rubric on their own artifact. This is the load-bearing governance rule for audit quality.

**Required:** The rubric must be run by a separate Grader role in a distinct context. The Grader receives the skill artifact and the acceptance criteria (from the spec) — not the authoring session reasoning. This structurally eliminates the confirmation bias that causes the author to interpret ambiguous rubric elements charitably [generator-assessor-separation-in-skill-iteration].

"The skill-creator NEVER both generates and assesses the same artifact in the same context." [generator-assessor-separation-in-skill-iteration]

**Convenience erosion risk:** Under deadline pressure, authors skip the grader subagent and grade inline. The governance system must make separation the path of least resistance — for example, by gating the Enhancement Handoff Block (§10) on a grader-context signature.

---

## 7. Capability vs. Regression Evals [capability-vs-regression-eval-lifecycle]

### 7.1 Definition of Each

**Capability evals** measure new abilities the skill is being improved to acquire:
- Start at low pass rates (the skill currently struggles with these cases)
- Pass rates climb as the skill is iterated
- Replaced when they saturate (reach near-100%)

**Regression evals** lock in behaviors the skill already performs correctly:
- Maintained at near-100% pass rates
- Any failure is a blocker — regression is unacceptable
- Accumulated over the skill's history from graduated capability evals

### 7.2 Why Both Are Needed

Without the split, teams "conflate improvement signal with stability signal":
- Saturated capability evals make progress appear artificially slow
- Unmaintained regression suites let previously-working features silently degrade [capability-vs-regression-eval-lifecycle]

Qodo found one-shot evals masked substantial progress on longer agentic tasks — single-track evals systematically hide the dimension of improvement that matters most [capability-vs-regression-eval-lifecycle].

### 7.3 Graduation Thresholds

A capability eval **graduates to the regression suite** when:
- The skill achieves near-100% pass rate **consistently** (not just on one run)
- The graduation is documented with the date, skill version, and eval case set

After graduation:
- The graduated eval cases join the regression suite
- New, harder capability evals replace them
- The capability suite always targets areas where the skill currently struggles

**Primary failure mode:** Over-graduating — moving evals to regression too early based on a few good runs rather than sustained performance. A threshold of 3+ consecutive runs at ≥95% before graduation reduces false promotions [capability-vs-regression-eval-lifecycle].

---

## 8. Description Optimization Eval Design [skill-description-optimization-loop-held-out-test]

Skill triggering is a classification problem. The description optimization loop treats it as one: held-out test sets, multiple runs per query, iteration with selection by test score.

### 8.1 The 20-Query Eval Set

Construct exactly 20 eval queries per skill:

- **8-10 should-trigger queries:** Requests where this skill SHOULD activate. Focus on **near-misses** — paraphrases, casual phrasing, queries that use different words than the description but mean the same thing.
- **8-10 should-not-trigger queries:** Requests where this skill MUST NOT activate. Focus on near-misses — queries that use similar words but should route to a different skill or no skill at all.

### 8.2 60/40 Train/Test Split

- **Train set (60%):** ~12 queries used during iteration. The description is optimized against these queries.
- **Test set (40%):** ~8 queries held out until the end. The best description is selected by TEST score only, not train score.

This prevents overfitting: a description optimized only against the train set may perfectly trigger on train queries while failing on the held-out test queries [skill-description-optimization-loop-held-out-test].

### 8.3 Iteration Protocol

- Run each train query **3 times** (triggering is non-deterministic; 3 runs reduces variance)
- Maximum **5 iterations** of description revision
- Select the description with the best **TEST score** — not the highest train score
- If no iteration improves the test score by ≥5%, stop and accept the current best

### 8.4 What Makes a Good Eval Query

> "Bad eval queries lead to bad descriptions." [skill-description-optimization-loop-held-out-test]

**Good queries are:**
- Specific (include file paths, company names, personal context where relevant)
- Realistic (how a user would actually phrase the request in the field)
- Casual (not formal task descriptions; use natural speech)
- Near-miss-focused (testing the decision boundary, not the obvious center)

**Bad queries:**
- "Format this data" (too generic)
- "Please analyze the attached report and provide a summary" (formal task description)
- Queries identical to the description's wording (testing recall, not discrimination)

**Structural constraint:** Claude only triggers skills it cannot handle alone. Simple single-step queries may not trigger even with a perfect description; eval queries must be complex enough that skill invocation provides genuine value [skill-description-optimization-loop-held-out-test].

---

## 9. Verification Levels [two-level-verification-agent-run-plus-harness-inte] [bmad-deterministic-skill-validator]

Two distinct verification levels must both be present. The prior "audit/design symmetry" framing is replaced by this finding-grounded distinction.

### Level 1: Deterministic Structural Validation [bmad-deterministic-skill-validator]

**What:** Automated, deterministic rule checks on the skill file's structure. Zero inference cost. Consistent across runs.

**When:** Runs in CI/CD before any merge; must pass before Level 2 evaluation is meaningful.

**BMAD reference implementation:** 19 rules across 6 categories:
1. **Naming conventions** — name field constraints, file naming (`SKILL.md` uppercase)
2. **Variable usage** — no undeclared variables, no reserved words
3. **Path references** — relative paths only; no absolute paths; no internal path leakage (PATH-05 encapsulation)
4. **Invocation syntax** — correct skill invocation language (REF-03)
5. **Sequence correctness** — required sections present in correct order
6. **Encapsulation boundaries** — no leaking of internal implementation paths

**CLI:** `skills-ref validate ./skill-directory` [skill-frontmatter-validation-rules]

**Critical limitation:** "Deterministic rules cannot catch semantic errors — a file passing all 19 structural rules may still produce incorrect behavior when executed." [bmad-deterministic-skill-validator] Level 1 passing is necessary but not sufficient.

### Level 2: LLM-Based Content Evaluation (Four-Discipline Rubric)

**What:** The four-discipline rubric applied by a separate Grader context to evaluate the skill's semantic quality.

**When:** After Level 1 passes; run by a Grader role in a context distinct from the author's.

**Two sub-levels within Level 2:**

- **Level 2a (Agent Run Verification):** Did the skill produce correct output? The Grader evaluates the skill's output against acceptance criteria using binary pass/fail assertions [verification-agent-seven-prompt-patterns].
- **Level 2b (Harness Integrity Verification):** When CLAUDE.md, hooks, skills, or settings change, do all existing guardrails still hold? This is a regression test suite for the harness configuration itself, not for any specific skill run [two-level-verification-agent-run-plus-harness-inte].

**Level 2b example checks (verbatim):** [two-level-verification-agent-run-plus-harness-inte]
- "Do destructive tools still require approval after this CLAUDE.md change?"
- "When tokens run out, does the agent gracefully stop or hard crash?"
- "Are permission boundaries still enforced after adding a new skill?"
- "Does the session persistence mechanism still work after updating hooks?"

"The harness evolves over time, and each evolution can silently break previously working safety properties. Level 2 verification catches these regressions." [two-level-verification-agent-run-plus-harness-inte]

### Level Sequencing

```
Skill artifact
     │
     ▼
Level 1: Deterministic structural validation
     │  FAIL → Fix structural violations, re-run
     │  PASS
     ▼
Level 2a: Four-discipline rubric (by separate Grader)
     │  FAIL → Enhancement Handoff Block (§10), iterate
     │  PASS
     ▼
Level 2b: Harness integrity check (if any config changed)
     │  FAIL → Revert config change or fix regression
     │  PASS
     ▼
Skill cleared for deployment
```

---

## 10. Enhancement Handoff Block [four-discipline-prompt-evaluator]

The Enhancement Handoff Block is the structured output the audit produces for downstream enhancement workflows. It is the communication protocol between the Grader and the Generator (or human author). Its structure ensures evaluation is actionable, not just diagnostic.

### 10.1 Handoff Block Format

```
AUDIT RESULT: [PASS | NEEDS REVISION | FAIL]
Skill name: <skill-name>
Audit date: <ISO date>
Grader context: <grader invocation ID, NOT the authoring session>

DISCIPLINE SCORES
─────────────────
Prompt Craft:              [PASS / FAIL] — <element that failed, if any>
Context Engineering:       [1-5] / 5 — bottleneck dimension: <dimension name>
Intent Engineering:        [1-5] / 5 — bottleneck dimension: <dimension name>
Specification Engineering: [1-5] / 5 — bottleneck dimension: <dimension name>

PRIORITY FIXES (in dependency order)
─────────────────────────────────────
1. [Discipline: <name>] <Specific fix required>
   Evidence: <Quote or example from the skill that demonstrates the issue>

2. [Discipline: <name>] <Specific fix required>
   Evidence: <Quote or example>

[continue for each identified issue]

WHAT NOT TO CHANGE
───────────────────
<List elements that scored well and must be preserved during revision>

EVAL COVERAGE GAPS
──────────────────
Missing capability eval cases: <description>
Missing regression coverage: <description>
Description eval status: <completed / not completed / needs refresh>

CLEARANCE CONDITIONS
────────────────────
This skill may be re-submitted for audit when:
[ ] <Fix 1 is addressed>
[ ] <Fix 2 is addressed>
[ ] Level 1 validation re-passes
```

### 10.2 Handoff Block Principles

- **Actionable, not just diagnostic.** Each priority fix must be specific enough that the Generator can act on it without asking the Grader for clarification [four-discipline-prompt-evaluator].
- **Evidence-cited.** Each fix must quote or reference the specific text in the skill that demonstrates the issue. "Improve the constraints section" is not actionable; "The constraint 'be professional' in line 47 is a positive aspiration; rewrite as a negative constraint" is [negative-constraints-as-probabilistic-output-collapse].
- **Preserves what works.** The "What Not to Change" section prevents the Generator from inadvertently breaking elements that scored well during revision.
- **Ordered by dependency.** Fixes are listed in discipline dependency order (Prompt Craft issues before Context issues). A Generator who fixes in this order will not need to revisit lower-layer fixes after addressing higher-layer ones [four-discipline-prompt-evaluator].
- **Grader context signature required.** The handoff block must record that it was produced in a context distinct from the authoring session. This is the governance evidence for generator-assessor separation [generator-assessor-separation-in-skill-iteration].

---

## Summary: Rubric Scoring Quick Reference

| Dimension | Scoring type | Minimum to deploy |
|-----------|-------------|------------------|
| Prompt Craft: Role | Pass/Fail | Pass |
| Prompt Craft: Task clarity | Pass/Fail | Pass |
| Prompt Craft: Output format | Pass/Fail | Pass |
| Prompt Craft: Constraints | Pass/Fail | Pass |
| Prompt Craft: Success criteria | Pass/Fail | Pass |
| Prompt Craft: Self-check | Pass/Fail | Pass |
| Context Engineering: Source scoping | 1-5 | ≥ 4 |
| Context Engineering: Signal-to-noise | 1-5 | ≥ 4 |
| Context Engineering: Dynamic vs static | 1-5 | ≥ 3 |
| Context Engineering: Memory/state | 1-5 | ≥ 3 |
| Intent Engineering: Goal explicitness | 1-5 | ≥ 4 |
| Intent Engineering: Constraint architecture | 1-5 | ≥ 4 |
| Intent Engineering: Klarna test | 1-5 | ≥ 3 |
| Intent Engineering: Stop rules | 1-5 | ≥ 4 |
| Spec Engineering: Self-containment | 1-5 | ≥ 4 |
| Spec Engineering: Acceptance criteria | 1-5 | ≥ 4 |
| Spec Engineering: Task decomposition | 1-5 | ≥ 3 |
| Spec Engineering: Evaluation design | 1-5 | ≥ 3 |
