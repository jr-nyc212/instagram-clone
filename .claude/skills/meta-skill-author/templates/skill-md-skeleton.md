<!--
TEMPLATE: SKILL.md skeleton with embedded elicitation
============================================================
This is a fill-in scaffold for authoring a new skill in Design mode (§1).
The HTML comment blocks marked <!-- TACIT KNOWLEDGE PROMPT --> are embedded
per-section elicitation instructions: answer them collaboratively, section by
section, instead of dumping a finished document at once
[yaml-templates-with-embedded-elicitation-instructions].

DELETE every comment block before publishing. The validator
(scripts/validate.sh) will WARN if elicitation comments remain.

Open-standard fields only by default. Add Claude Code extension fields
(when_to_use, paths, disable-model-invocation, ...) ONLY if the skill is
non-portable, and declare `compatibility` when you do
[skills-as-open-portable-standard].
============================================================
-->
---
name: <lowercase-hyphenated-name>          # 1–64 chars, [a-z0-9-], matches dir, no "anthropic"/"claude"
description: >
  <!-- TACIT KNOWLEDGE PROMPT: Write [What it does] + [When to use it] +
       [Key capabilities]. Put the key use case FIRST (survives truncation).
       Include real trigger phrases and file types. Be "a little bit pushy" to
       combat undertriggering. Hard cap 1,024 chars; no XML tags.
       [skill-description-structure-what-when-capabilities]
       [skill-md-frontmatter-as-discovery-trigger-primitive] -->
license: MIT
# compatibility: <declare only if using non-portable extension fields>
---

## Objective & Why
<!-- TACIT KNOWLEDGE PROMPT: One sentence — what outcome does this skill produce,
     and why does it matter? This is the Intent Engineering anchor.
     [intent-engineering-framework-seven-part-agent-inten] -->

## Desired Outcomes (2–4)
<!-- TACIT KNOWLEDGE PROMPT: List 2–4 concrete, observable outcomes a successful
     run produces. Not activities — outcomes. -->

## Authoritative Inputs
<!-- TACIT KNOWLEDGE PROMPT: What are the ONLY trusted inputs? Classify trust on
     any retrieved data. Point to references/ rather than embedding context
     [skill-as-package-export-with-references]. -->

## Procedure / Goal + Constraints
<!-- TACIT KNOWLEDGE PROMPT: Default to OUTCOME-BASED (goal + constraints) for
     interactive skills. Use numbered SOP steps ONLY for scheduled/unattended
     runs [hands-off-routine-prompt-precision-pattern].
     Do NOT add chain-of-thought, few-shot examples, or decomposition scaffolding
     — they degrade frontier reasoning models
     [reasoning-model-anti-pattern-prescribed-reasoning].
     Express rules as NEGATIVE constraints and explain the WHY; avoid ALL-CAPS
     MUST stacks [negative-constraints-as-probabilistic-output-collapse]
     [skill-authoring-explain-the-why-not-musts]. -->

## Constraints (must / must-not / escalate-if)
<!-- TACIT KNOWLEDGE PROMPT: Separate steering constraints from hard constraints.
     What must never happen? When must the agent escalate instead of acting? -->

## Stop Rules
<!-- TACIT KNOWLEDGE PROMPT: The MOST COMMONLY OMITTED intent component. Under
     what conditions must the agent halt and ask rather than proceed? Always fill
     this in [intent-engineering-framework-seven-part-agent-inten]. -->

## Side Effects, Reversibility & HITL Tier
<!-- TACIT KNOWLEDGE PROMPT: For each action with a side effect, classify
     reversibility (fully reversible / reversible-with-effort / practically
     irreversible / irreversible) and assign an autonomy tier
     (Full Autonomy / Guarded / Proposal-first / Human-required) using the
     blast-radius × reversibility matrix
     [autonomy-gradient-not-binary-delegation]
     [agent-action-reversibility-as-design-requirement]. -->

## Acceptance Criteria (verifiable)
<!-- TACIT KNOWLEDGE PROMPT: Binary, testable pass/fail conditions. "Good output"
     is not testable; "every claim cites a source" is. These anchor your evals. -->

## Output Format
<!-- TACIT KNOWLEDGE PROMPT: Exact structure of the deliverable. At decision
     gates, prefer HTML over Markdown so humans actually read it
     [html-output-as-human-in-the-loop-restorer]. -->

## Evaluation
<!-- TACIT KNOWLEDGE PROMPT: Evaluation is run ON DEMAND by the meta-tool, which
     writes a SIBLING "<skill-name>-workspace/" — do NOT bake eval files or run
     outputs into the skill itself (the skill is the input, the workspace holds the
     evals and results). Scaffold the workspace with:
       bash scripts/eval.sh --init ./<skill-dir>            (objective skills)
       bash scripts/eval.sh --init --subjective ./<skill-dir>  (writing/voice/design/art)
       bash scripts/eval.sh --init --deterministic ./<skill-dir>  (script-core: renderer/parser/validator)
     Every skill gets a triggering / description eval (objective). ONLY objectively-
     verifiable skills (file transforms, extraction, codegen, fixed steps) add binary
     capability assertions; SUBJECTIVE skills (writing style, voice, art) are evaluated
     QUALITATIVELY with a named scorecard + a human review loop; DETERMINISTIC/script-core
     skills (a tested renderer/parser/validator) are verified by the script's own tests +
     Level 1 — do not force LLM assertions onto either
     [audit-rubric.md §5 subjective-skill + deterministic/script-core carve-outs].
     Grading is done by a SEPARATE Grader context (agents/grader.md against
     references/audit-rubric.md), never self-graded
     [generator-assessor-separation-in-skill-iteration]. -->

<!--
BEFORE PUBLISHING — Definition of Done (a skill is not "done" until all are true):
1. Delete all TACIT KNOWLEDGE PROMPT comment blocks.
2. Keep SKILL.md under 500 lines; front-load critical content.
3. Run the readiness gate (scaffolds the sibling workspace):
   bash scripts/eval.sh --init [--subjective|--deterministic] ./<skill-dir>
4. Fill the workspace's trigger-eval-set.md (all skills); for objective skills also fill
   eval-cases.md; for subjective skills document the qualitative scorecard + review loop;
   for deterministic/script-core skills ensure the bundled script tests pass.
5. Re-run bash scripts/eval.sh [--subjective|--deterministic] ./<skill-dir>  until it reports READY.
6. Run the description optimization loop (templates/eval-query-set.md); select the
   winner by TEST score [skill-description-optimization-loop-held-out-test].
7. Hand to a SEPARATE Grader context using agents/grader.md for the four-discipline
   rubric — never self-grade [generator-assessor-separation-in-skill-iteration].
8. Record the AUDIT RESULT (PASS, or handoff fixes applied) in the package CHANGELOG.
-->
