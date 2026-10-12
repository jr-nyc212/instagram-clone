# Skill-Authoring Anti-Patterns Reference

> Reference doc for the cross-AI skill-authoring meta-skill.
> 14 cataloged anti-patterns, each with: what it looks like / why it fails / fix / finding citation.
> Every claim cites a finding from the master inventory.

---

## How to Use This Catalog

Each anti-pattern follows a four-section block:

- **What it looks like** — concrete observable signal
- **Why it fails** — the mechanism of failure
- **Fix** — concrete remediation
- **Citation** — the finding(s) that ground the claim

These 14 replace the prior draft's six anti-patterns. Sources: §2.11 of the master inventory plus supplementary findings across all buckets [findings-master-inventory].

---

## AP-01: Self-Grading by Author (No Generator-Assessor Separation)

### What it looks like
The same session, agent, or context that authored the skill also evaluates whether the skill is good. The author runs the rubric on their own artifact and declares it passing.

### Why it fails
"The skill-creator NEVER both generates and assesses the same artifact in the same context." Shared context creates confirmation bias: the evaluator has access to the author's reasoning chain and interprets ambiguous outputs charitably. Practitioners report that same-window verification consistently misses errors that independent judges catch [llm-as-judge-pattern-for-verification-agents]. Under deadline pressure this collapses under exactly the conditions where the discipline matters most — "convenience erosion" [generator-assessor-separation-in-skill-iteration].

### Fix
Implement five-role separation in distinct contexts: Generator (author) → Executor (runs skill per eval case) → Grader (reads grader.md, evaluates assertions) → Comparator (blind A/B between skill versions) → Analyzer (fresh context, explains why one version beat the other). The Grader receives assertions from the spec — the spec defines what good looks like, not the Grader. The Comparator does not know which output is which (defeats positional bias) [generator-assessor-separation-in-skill-iteration].

### Citation
[generator-assessor-separation-in-skill-iteration], [llm-as-judge-pattern-for-verification-agents]

---

## AP-02: ALL-CAPS MUSTs Without WHY

### What it looks like
```
ALWAYS include a summary section.
NEVER call external APIs without checking the cache first.
YOU MUST validate the input before proceeding.
```
Constraints expressed as imperatives without explanations of their purpose.

### Why it fails
"Today's LLMs are smart. They have good theory of mind and when given a good harness can go beyond rote instructions." ALL-CAPS imperatives prevent the model from extending rules to edge cases: if the model does not know why a constraint exists, it cannot determine whether the constraint applies in a novel situation the author did not anticipate. The rule becomes brittle and either over-applies (blocking legitimate actions) or under-applies (silently ignored in adjacent cases) [skill-authoring-explain-the-why-not-musts].

### Fix
For every constraint, add a one-sentence rationale: "Always include a summary section **because downstream consumers parse the summary field programmatically**." Reserve ALL-CAPS for non-negotiable security or format requirements — and even then, add the rationale alongside the constraint, not replacing it. Discipline required: explaining reasoning adds tokens; only consequential decisions need it [skill-authoring-explain-the-why-not-musts].

### Citation
[skill-authoring-explain-the-why-not-musts]

---

## AP-03: CoT/Few-Shot in Instructions for Reasoning Models

### What it looks like
A skill body includes:
- Numbered chain-of-thought scaffolding ("Step 1: Think about the problem...")
- Few-shot examples embedded as reasoning demonstrations
- Self-consistency instructions ("Generate three versions and pick the best")
- Least-to-most decomposition ("First solve the simpler case, then extend")
- Skeleton-of-thought templates

### Why it fails
On reasoning models (GPT-5.4, Claude 4.6, Gemini 3.1), these five techniques **degrade performance**. They are a "breaking change in prompting convention" [reasoning-model-anti-pattern-prescribed-reasoning]. Reasoning models already perform internal chain-of-thought; explicit CoT scaffolding in the prompt introduces interference with the model's native reasoning process. The techniques were designed for non-reasoning models and are now harmful on all three frontier model families.

### Fix
Replace prescribed reasoning structures with the Goal + Constraints + Context pattern. Use declarative outcome-based instructions rather than imperative step-by-step procedures [declarative-goal-driven-agent-prompting]. The audit step for this anti-pattern: search the skill body for any numbered "Step X" reasoning sequences, few-shot example blocks, or self-consistency instructions and remove them.

### Citation
[reasoning-model-anti-pattern-prescribed-reasoning], [declarative-goal-driven-agent-prompting]

---

## AP-04: SKILL.md Over 500 Lines

### What it looks like
A SKILL.md body that has grown to 600, 800, or 1,200 lines through accumulated additions — each addition individually justified, but the aggregate bloated.

### Why it fails
Anthropic explicit guidance: keep SKILL.md under 500 lines [skill-as-directory-progressive-disclosure-three-levels]. The skill body enters conversation as one persistent message at activation; post-compaction, 5K tokens are preserved per skill with a 25K combined budget and LRU drop. Critical guidance past 5K tokens is at risk after compaction. ETH Zurich (438 tasks, 4 agents) found context files increase reasoning token usage 14-22% [context-file-instruction-bloat-eth-zurich]. A 700-line SKILL.md where 650 lines are irrelevant "dilutes the 50 relevant lines" [claudemd-as-signal-to-noise-problem-not-size-probl].

### Fix
Use progressive disclosure: SKILL.md carries only workflow instructions and file path pointers (≤500 lines). Deep reference content lives in `references/` and is loaded on demand via relative paths. The L0 abstract (~100 tokens) and L1 description (~2K tokens) are the always-loaded content; L2 full body is the 500-line cap; L3+ reference files are unbounded but demand-loaded [skill-as-directory-progressive-disclosure-three-levels].

### Citation
[skill-as-directory-progressive-disclosure-three-levels], [context-file-instruction-bloat-eth-zurich], [skill-content-lifecycle-context-budget]

---

## AP-05: Description Drift (Body Changes, Description Stale)

### What it looks like
A skill's SKILL.md body has been updated five times over the past month, but the frontmatter description still describes the original version's behavior. Triggering continues to work for the original use cases but silently fails for the new ones.

### Why it fails
Skill triggering is description-matching, not keyword extraction or hard rules. In auto-dispatch systems, description quality is **the only routing signal** [agent-description-auto-dispatch-routing]. "A perfect SKILL.md body that never triggers is dead capability" [skill-md-frontmatter-as-discovery-trigger-primitive]. Description drift is a silent failure mode: no error is thrown, the skill simply does not trigger when it should, and the new use cases remain inaccessible [description-based-workflow-routing-lazy-dispatch].

### Fix
Treat the description as a versioned artifact that must be updated every time the body changes in a way that affects when the skill should trigger. Add description review to the skill's PR checklist. Run the description optimization loop (AP-12's fix) after any substantial body change to verify triggering accuracy has not degraded [skill-description-optimization-loop-held-out-test].

### Citation
[description-based-workflow-routing-lazy-dispatch], [skill-md-frontmatter-as-discovery-trigger-primitive]

---

## AP-06: Overlapping Descriptions Between Skills

### What it looks like
Two skills in the same library have descriptions that both trigger on the same user request type. Example: a `research-web` skill and a `find-sources` skill both describe themselves as useful for "finding information on a topic."

### Why it fails
Overlapping descriptions cause systematic mis-routing. In auto-dispatch systems, the dispatcher must choose between the two; the choice is non-deterministic and does not reflect intent. The two skills compete for the same triggering signal, reducing both to lower effective accuracy than either would have alone. "Overlapping descriptions between skills cause systematic mis-routing" [agent-description-auto-dispatch-routing]. This failure is invisible in single-skill testing but surfaces only when both skills are in context simultaneously.

### Fix
Each skill's description must be discriminative: it must distinguish the skill from all other skills in the same library. Identify the specific trigger condition unique to each skill. Run negative eval queries from one skill's should-trigger set as should-not-trigger queries for the overlapping skill [skill-description-optimization-loop-held-out-test]. If two skills truly have identical trigger conditions, they should be merged into one skill with branching logic.

### Citation
[agent-description-auto-dispatch-routing], [skill-description-optimization-loop-held-out-test]

---

## AP-07: Embedding Context Copies Instead of Pointers

### What it looks like
A skill's SKILL.md body contains:
- A 200-line directory listing of the project structure
- Verbatim copies of configuration values also present in config files
- Embedded schema definitions that also exist in the codebase
- Copied reference text that exists in a shared context folder

### Why it fails
"Stale context is worse than no context" [pointers-over-copies-in-context-files]. Embedded copies create a synchronization problem: when the source-of-truth changes, the copy in SKILL.md does not. The agent may act on outdated information without knowing it is outdated. Additionally, ETH Zurich found agents are "surprisingly good at discovering file structures on their own" — directory listings in SKILL.md add overhead without benefit [pointers-over-copies-in-context-files]. Embedding copies also violates the size budget (AP-04).

### Fix
Skills should contain only workflow instructions and file path references to shared second-brain files [skills-as-pointers-to-second-brain-files]. Replace any embedded content with a relative path pointer: instead of the schema definition, write `See: ../references/schema.md`. Update propagates automatically: change one fact in the source file, every subsequent skill execution uses updated information [shared-context-folder-as-cross-skill-update-multiplier].

### Citation
[pointers-over-copies-in-context-files], [skills-as-pointers-to-second-brain-files]

---

## AP-08: Auto-Generated Context Files

### What it looks like
CLAUDE.md, AGENTS.md, or SKILL.md files that were produced by asking an AI to "write comprehensive instructions for this codebase" in a single pass. The files are verbose, cover every scenario the AI could imagine, and were not validated against real tasks.

### Why it fails
ETH Zurich (438 tasks, 4 agents) measured this directly: LLM-generated context files reduce task success rates approximately 3% and increase inference cost 20% compared to no context file at all. Even human-written context files add 14-22% reasoning token overhead. Claude Code was the only agent where even human-written context files failed to improve performance in some conditions [context-file-instruction-bloat-eth-zurich]. Auto-generated files are worse than human-written ones: they are verbose, include information the AI can discover itself, and dilute attention on the instructions that matter.

### Fix
Write context files manually. Apply the minimum-viable-rule discipline: each line must pass the test "would I manually type this into context at the start of nearly every session?" A CLAUDE.md of 3-5 globally-true, universally-relevant lines outperforms a comprehensive AI-generated one [claudemd-minimum-viable-rule-only-add-globally]. If generation is needed for scaffolding, treat the output as a first draft and aggressively prune to only the lines that carry genuine signal.

### Citation
[context-file-instruction-bloat-eth-zurich], [claudemd-minimum-viable-rule-only-add-globally], [claudemd-as-signal-to-noise-problem-not-size-probl]

---

## AP-09: Reserved Words / XML in Frontmatter

### What it looks like
```yaml
name: claude-assistant-helper
description: "Use <when> the user asks about <topic>. See <claude-docs> for reference."
```

### Why it fails
Frontmatter restrictions are prompt injection defenses, not style rules [skill-md-frontmatter-as-discovery-trigger-primitive]. The name field prohibits reserved words `anthropic` and `claude` because they can be used to impersonate trusted system skills. XML angle brackets in the description field create injection vectors: the description enters Claude's system prompt at startup, before any user interaction. Any XML-like structure in the description can be parsed as instructions by the model [skill-frontmatter-validation-rules]. These violations fail the `skills-ref validate` check.

### Fix
Use only lowercase a-z, 0-9, and hyphens in the name field. No reserved words. No leading, trailing, or consecutive hyphens. In the description field, write plain prose — no XML tags, no angle brackets, no structured markup. Run `skills-ref validate ./skill-directory` to catch violations before deployment [skill-frontmatter-validation-rules].

### Citation
[skill-md-frontmatter-as-discovery-trigger-primitive], [skill-frontmatter-validation-rules]

---

## AP-10: Side-Effect Skill Without disable-model-invocation

### What it looks like
A skill named `deploy-to-production` or `send-weekly-report` that has a normal frontmatter — no `disable-model-invocation: true` — and therefore is available for Claude to auto-trigger based on description matching during any session.

### Why it fails
Side-effect skills (commit, deploy, send communication, publish) must not be auto-triggered by description matching. Without `disable-model-invocation: true`, the skill can be triggered during a workflow where only a read operation was intended. The description is in Claude's context at all times, and any sufficiently close task match can trigger an irreversible action silently [skill-invocation-control-side-effect-guard]. This is the "allowed-tools grant inflation" vulnerability applied to invocation control.

### Fix
Add `disable-model-invocation: true` to all side-effect skills. This removes the description from context and requires explicit slash-command invocation by the user. The human must consciously type the command; the skill cannot be triggered as a side-effect of a broader workflow [skill-invocation-control-side-effect-guard].

### Citation
[skill-invocation-control-side-effect-guard], [skill-security-audit-obligation]

---

## AP-11: Spec-First When Tacit Knowledge Is Unstated

### What it looks like
An author is asked to write a skill for an expert practitioner's workflow. The author writes a spec immediately — "summarize the process, I'll write the spec from that." The result is a skill that handles the explicit, describable steps but misses the judgments that distinguish expert performance from novice performance.

### Why it fails
"Expertise compresses into automatic judgment even experts cannot articulate." A practitioner asked to describe their process will describe the surface-level steps but cannot consciously surface the micro-decisions that constitute mastery [tacit-knowledge-as-agent-delegation-barrier]. The resulting skill handles common cases but fails on exactly the cases where expert judgment is most valuable. Spec-first development starts from a specification the author cannot correctly write until the tacit knowledge is first externalized.

### Fix
Run the 5-layer tacit knowledge elicitation workflow (approximately 45 minutes) before writing any spec:
1. **Operating rhythms** — when does this work happen, at what cadence?
2. **Recurring decisions** — what choices are made repeatedly?
3. **Required inputs** — what information is needed at each step?
4. **Recurring friction points** — what goes wrong most often?
5. **Success criteria** — how do you know when the work is done well?

The elicitation output becomes the CONTEXT.md artifact that gates the Design phase [tacit-knowledge-as-agent-delegation-barrier]. Alternatively, use induction from examples: video transcripts of the expert doing the work produce more comprehensive results than manual specification [video-transcript-driven-voice-skill-generation].

### Citation
[tacit-knowledge-as-agent-delegation-barrier]

---

## AP-12: Single Eval Suite (No Capability/Regression Split)

### What it looks like
A skill has one eval suite. Improvements are measured by whether the overall pass rate goes up. A new skill version that fixes three new cases but breaks one previously-passing case still shows a net improvement in the overall score.

### Why it fails
A single eval suite "conflates improvement signal with stability signal." Without the split:
- **Saturated capability evals make progress appear artificially slow**: once all the easy cases pass, the eval no longer shows improvement even when real progress is happening on harder cases.
- **Unmaintained regression suites let previously-working features silently degrade**: a skill change that breaks established behavior passes if new capability cases outnumber the regressions [capability-vs-regression-eval-lifecycle].

SWE-Bench Verified went from ~40% to >80% in one year and is approaching saturation — the same phenomenon will happen with any single-track eval suite [capability-vs-regression-eval-lifecycle].

### Fix
Maintain two distinct eval tracks:
- **Capability evals:** Start at low pass rates; measure new abilities; replaced when they saturate.
- **Regression evals:** Near-100% pass rate required; lock in known-good behaviors; any failure is a blocker.

Graduation threshold: when a capability eval hits 100% consistently, move it to the regression suite and add harder new capability evals to replace it. Over-graduating — moving evals to regression too early based on a few good runs — is the primary failure mode [capability-vs-regression-eval-lifecycle].

### Citation
[capability-vs-regression-eval-lifecycle]

---

## AP-13: Positive Constraints Instead of Negative for Behavior Rules

### What it looks like
```
Try to be confident in your responses.
Aim for a professional tone.
Prefer concise answers when possible.
```

Rules expressed as positive aspirations rather than negative prohibitions.

### Why it fails
Negative constraints ("never begin with an apology") **collapse the probability distribution** of outputs. Positive guidance ("try to be confident") only weakly biases the distribution — it adds weight to the desired behaviors but does not meaningfully reduce the probability of the undesired ones [negative-constraints-as-probabilistic-output-collapse]. For behavioral rules that must be reliably followed, positive framing leaves significant probability mass on the undesired side.

### Fix
Express behavioral rules as negative constraints for maximum reliability:
- "Try to be confident" → "Do not hedge every statement with uncertainty markers"
- "Professional tone" → "Do not use casual slang or emoji"
- "Prefer concise" → "Do not repeat the user's question back to them; do not include preamble before answering"

Negative constraints are appropriate for **behavioral rules**. Positive framing is appropriate for **goals and outcomes** where flexibility is desirable. The distinction: constraints on style/format → negative; goals for output quality → positive [negative-constraints-as-probabilistic-output-collapse].

### Citation
[negative-constraints-as-probabilistic-output-collapse]

---

## AP-14: Procedural Step-by-Step Where Outcome-Based Works

### What it looks like
```
1. First, read the input file and identify the key entities.
2. Then, cross-reference each entity against the database.
3. Next, score each entity by relevance to the query.
4. Finally, return the top 5 scored entities formatted as JSON.
```
Imperative numbered steps describing the execution path rather than the desired outcome.

### Why it fails
Declarative (outcome-based) instructions outperform imperative (step-by-step) for interactive use cases because LLMs are architecturally built to loop until they meet goals — prescribing the loop path adds overhead without benefit [declarative-goal-driven-agent-prompting]. BMAD's outcome-based skill rewrite produced approximately 50% token reduction versus procedural format for the same skill [bmad-outcome-based-skill-rewrite-pattern]. On reasoning models, procedural instructions conflict with the model's native reasoning process (AP-03) [reasoning-model-anti-pattern-prescribed-reasoning].

### Fix
For **interactive skills**, rewrite as outcome-based:
```
Return the 5 most relevant entities from the database for this query,
ranked by relevance score, formatted as JSON with fields:
entity_id, name, relevance_score (0-1), match_reason.
```

**Exception:** Skills intended for unattended scheduled execution (cron jobs, automated pipelines) should retain SOP-style numbered steps with explicit completion signals and inline edge-case handling [hands-off-routine-prompt-precision-pattern]. The design-time question: "Is this skill interactive or scheduled?" determines which format applies (see Contradiction C7 in the master inventory [findings-master-inventory]).

### Citation
[declarative-goal-driven-agent-prompting], [bmad-outcome-based-skill-rewrite-pattern], [reasoning-model-anti-pattern-prescribed-reasoning]

---

## Quick Reference Matrix

| # | Anti-pattern | Signal | Primary fix |
|---|--------------|--------|-------------|
| AP-01 | Self-grading | Same context authors + evaluates | Five-role separation |
| AP-02 | ALL-CAPS MUSTs | No WHY with constraints | Add rationale to every constraint |
| AP-03 | CoT/few-shot for reasoning models | Numbered reasoning steps or example blocks | Goal + Constraints + Context |
| AP-04 | SKILL.md > 500 lines | Body over 500 lines | Progressive disclosure to references/ |
| AP-05 | Description drift | Stale frontmatter after body edits | Description update on every body change |
| AP-06 | Overlapping descriptions | Two skills trigger on same request | Discriminative descriptions + negative eval |
| AP-07 | Context copies | Embedded schema/config/directory | Path pointers to shared sources |
| AP-08 | Auto-generated context | AI wrote CLAUDE.md/SKILL.md | Manual authoring with minimum-viable-rule |
| AP-09 | Reserved words / XML in frontmatter | `claude-` prefix or `<tags>` | Plain prose, `skills-ref validate` |
| AP-10 | Side-effect without disable-model-invocation | Deploy/commit skill auto-triggerable | `disable-model-invocation: true` |
| AP-11 | Spec-first without tacit knowledge | Skill misses expert judgments | 5-layer elicitation before spec |
| AP-12 | Single eval suite | One mixed eval track | Capability + regression split |
| AP-13 | Positive behavioral constraints | "Try to be..." rules | Rewrite as "Do not..." rules |
| AP-14 | Procedural for interactive use | Numbered steps for non-scheduled skill | Outcome-based rewrite |
