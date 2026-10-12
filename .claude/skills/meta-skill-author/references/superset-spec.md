# Superset Spec: Complete Field Reference for Cross-AI Skills

**Purpose:** The authoritative superset of all SKILL.md fields and body-structure rules spanning five platforms — Claude Code, Cursor, GitHub Copilot, OpenAI Codex, and Perplexity. Every field is tagged **portable** (defined by the open standard) or **harness-specific** (Claude Code extension). Where a field is proposed by findings but not yet in any shipping spec, it is tagged **proposed**.

---

## 1. Frontmatter — Open Standard Fields (portable)

The Agent Skills open standard was published by Anthropic at agentskills.io on December 18, 2025 under Apache 2.0 (code) / CC-BY-4.0 (docs). Explicit analogy to MCP: "Like MCP, we believe skills should be portable across tools and platforms." [skills-as-open-portable-standard]

These six fields constitute the portable floor. Any skill that uses only these fields can be consumed by any conformant harness. [skills-as-open-portable-standard]

### 1.1 `name` — **portable**

| Constraint | Rule |
|------------|------|
| Length | 1–64 characters |
| Character class | `[a-z0-9-]` only (lowercase letters, digits, hyphens) |
| Leading/trailing | No leading or trailing hyphens |
| Consecutive | No consecutive hyphens (`--` forbidden) |
| Directory match | Must match the parent directory name exactly |
| Reserved words | `anthropic` and `claude` are forbidden anywhere in the name |
| XML prohibition | No XML angle brackets (`<`, `>`) |
| File name | File must be named `SKILL.md` (all uppercase); lowercase `skill.md` fails upload [skill-md-format-yaml-front-matter-requirements] |

Rationale for restrictions: character-class limits and XML-tag prohibition are prompt-injection defenses; reserved-word ban prevents impersonation. [skill-frontmatter-validation-rules]

> "The same skill should work whether you're using Claude or another AI platform." [skills-as-open-portable-standard]

Validation: run `skills-ref validate ./my-skill` to catch naming violations mechanically. [skill-frontmatter-validation-rules]

### 1.2 `description` — **portable**

| Constraint | Rule |
|------------|------|
| Length | 1–1,024 characters (open standard cap) |
| Combined cap (Claude Code) | `description` + `when_to_use` together ≤ 1,536 characters per entry [skill-description-budget-context-overflow] |
| Recommended target | ≤ 800 characters for `description` alone, leaving room for `when_to_use` |
| XML prohibition | No XML tags |
| Non-empty | Must not be blank |

> **Contradiction C1 clarified:** The 1,024-character limit governs the `description` field alone (open standard). The 1,536-character limit governs the combined `description` + `when_to_use` budget within Claude Code. These are not contradictory; they govern different fields. Authors should target ≤ 800 characters for `description`. [§3 C1 of master inventory]

**Canonical three-part structure:** [What it does] + [When to use it] + [Key capabilities] [skill-description-structure-what-when-capabilities]

**Good example (verbatim from finding):**
> "Analyzes Figma design files and generates developer handoff documentation. Use when user uploads .fig files, asks for 'design specs', 'component documentation', or 'design-to-code handoff'." [skill-description-structure-what-when-capabilities]

**Three named failure modes:**
1. Too vague — "Helps with projects" [skill-description-structure-what-when-capabilities]
2. Missing triggers — "Creates sophisticated multi-page documentation systems" [skill-description-structure-what-when-capabilities]
3. Too technical, no user triggers — "Implements the Project entity model with hierarchical relationships" [skill-description-structure-what-when-capabilities]

**Discovery primitive:** The frontmatter alone enters Claude's system prompt at startup; the body is filesystem-resident until activation. A perfect SKILL.md body that never triggers is dead capability. [skill-md-frontmatter-as-discovery-trigger-primitive]

**Context budget:** `skillListingBudgetFraction` = 0.01 (1% of context window) for all descriptions combined; `maxSkillDescriptionChars` = 1,536 per entry; past the cap, descriptions are truncated and keywords strip before Claude sees them. Survival rule: "Put the key use case first." [skill-description-budget-context-overflow]

**Pushy language:** Skill-creator recommends "a little bit pushy" language (e.g., "Make sure to use this skill whenever...") to combat Claude's documented undertriggering bias. The Complete Guide PDF uses a more neutral baseline. The meta-skill endorses pushy as the default; the optimization loop validates which level actually improves TEST scores. [skill-md-frontmatter-as-discovery-trigger-primitive][skill-description-optimization-loop-held-out-test]

**Prompt injection risk:** MCP tool descriptions and skill descriptions are model-readable metadata and an active attack surface. Treat all descriptions as trusted, validated content. Character-class restrictions and XML-tag prohibition are the defense layer. [mcp-tool-description-prompt-injection-attack][skill-md-frontmatter-as-discovery-trigger-primitive]

### 1.3 `license` — **portable**

Optional. No mechanical constraint specified by the open standard. Recommended: declare explicitly for skills intended for distribution (e.g., `MIT`, `Apache-2.0`). [skill-frontmatter-validation-rules]

### 1.4 `compatibility` — **portable**

Optional. ≤ 500 characters. Declares surface requirements for non-portable skills. [skill-frontmatter-validation-rules]

Use when a skill requires Claude Code-specific features not available on other surfaces:
- `claude.ai`: folder + zip required for upload; no Claude Code extensions work [skill-cross-surface-portability-with-constraints]
- `claude-api`: no network, pre-installed packages only; beta headers required [skill-cross-surface-portability-with-constraints]
- `claude-code`: full network, local installs, filesystem-based; full extension set available [skill-cross-surface-portability-with-constraints]

Custom skills do NOT sync across surfaces; each deployment is independent. [skill-cross-surface-portability-with-constraints]

### 1.5 `metadata` — **portable**

Optional key-value map. No mechanical constraint specified by the open standard. [skill-frontmatter-validation-rules]

### 1.6 `allowed-tools` — **portable (Experimental)**

Optional. Pre-approves tools without per-invocation prompting. Trust dialog grants authority silently — accepting a workspace trust dialog for a skill with broad `allowed-tools` grants that authority without further confirmation. [claude-code-skill-frontmatter-extensions]

> **Anti-pattern:** `allowed-tools: Bash(*) Read Write` in a checked-in project skill grants broad authority after a single workspace trust dialog — "allowed-tools grant inflation." [skill-security-audit-obligation]

---

## 2. Frontmatter — Claude Code Extension Fields (non-portable)

These ~13 fields are Claude Code-specific and not in the open-standard validation table. Skills using any of these fields are silently non-portable and should declare `compatibility: claude-code`. [claude-code-skill-frontmatter-extensions]

| Field | Semantic |
|-------|----------|
| `when_to_use` | Natural-language guidance for when Claude should activate this skill; part of the 1,536-char combined budget with `description` |
| `argument-hint` | Hint shown in `/` menu for invocation arguments |
| `arguments` | Declared argument structure; enables `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, `$name` substitution in body |
| `disable-model-invocation` | `true` → Claude cannot auto-load; description NOT in context; use for side-effect skills (commit, deploy, send-slack). "You don't want Claude deciding to deploy because your code looks ready." [skill-invocation-control-side-effect-guard] |
| `user-invocable` | `false` → user cannot invoke via `/`; Claude can; description IS in context; for background-knowledge skills [skill-invocation-control-side-effect-guard] |
| `disallowed-tools` | Tools explicitly blocked during skill execution |
| `model` | Override the model used for this skill's execution |
| `effort` | Effort level; available via `${CLAUDE_EFFORT}` substitution in body |
| `context` | `fork` → spawns isolated subagent; skill body becomes the task prompt; named agent provides system prompt; no access to main conversation history [skill-forked-subagent-execution] |
| `agent` | Target agent type for `context: fork` (`Explore`, `Plan`, custom `.claude/agents/<name>.md`) |
| `hooks` | Event hooks (pre/post invocation) |
| `paths` | File-glob patterns gating auto-load; skills silently won't auto-load on non-matching files [claude-code-skill-frontmatter-extensions] |
| `shell` | Shell command executed at the skill level |

**Key semantic rules:**
- `disable-model-invocation: true` removes the description from Claude's context entirely, freeing skill-listing budget for other skills. [skill-invocation-control-side-effect-guard]
- `user-invocable: false` + `disable-model-invocation: true` = unreachable from any actor. [claude-code-skill-frontmatter-extensions]
- `paths` gating is silent — authors must test that skills activate on all intended file types. [claude-code-skill-frontmatter-extensions]
- A skill with `context: fork` must include explicit task instructions in its body, not just guidelines. A fork subagent receives the skill body as its task prompt; guideline-only content returns without meaningful output. [skill-forked-subagent-execution]
- A skill targeting `agent: Explore` must not assume project CLAUDE.md conventions are loaded — they are not on Explore/Plan agents. [skill-forked-subagent-execution]

**Shell substitutions (body-level):** `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, `$name` (via declared arguments), `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}`. [claude-code-skill-frontmatter-extensions]

**Dynamic context injection:** `` !`<command>` `` syntax runs shell commands at skill activation time (once, one-pass substitution) and inserts stdout into the rendered SKILL.md before Claude sees any content. A malicious skill could embed exfiltration via this channel. `disableSkillShellExecution: true` in settings disables it. [skill-dynamic-context-injection-shell-prerender]

---

## 3. Body Sections — Required Five-Element Model

Frame the skill as an onboarding document for a new employee — this mental model naturally produces complete instructions. [skill-as-new-employee-mental-model]

The five required elements:

1. **Purpose / scope** — What this skill does and its boundaries
2. **Triggering conditions** — When the skill applies and what context is provided at invocation
3. **Step-by-step instructions with branching logic** — For scheduled/unattended skills; for interactive skills, use outcome-based framing instead (see §4)
4. **Internal policies and constraints** — Hard rules and the WHY behind them
5. **Precise format and content of expected output** — As reliability engineering, not readability
[skill-as-new-employee-mental-model]

**Five-layer completeness checklist** (audit each authored skill against all five):
1. Role & Scope
2. Instructions & Constraints (with trust classification on retrieved data)
3. Context & Retrieved Data
4. Examples & Edge Cases (including adversarial cases)
5. Output Format & Tool-Calling
[five-layer-agent-prompt-architecture]

> "Agent prompt engineering is a systems problem. Prompt quality depends on how well retrieval, tools, and memory are scoped and orchestrated, not just how polished the prompt verbiage is." [five-layer-agent-prompt-architecture]

**Explain the WHY:**
> "Try hard to explain the why behind everything you're asking the model to do. Today's LLMs are smart. They have good theory of mind and when given a good harness can go beyond rote instructions and really make things happen." [skill-authoring-explain-the-why-not-musts]
>
> "If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid structures, that's a yellow flag — if possible, reframe and explain the reasoning so that the model understands why the thing you're asking for is important." [skill-authoring-explain-the-why-not-musts]

Explaining reasoning adds tokens; apply this discipline only for consequential decisions. Some constraints (security, format requirements) are non-negotiable and require reasoning explanations alongside the constraint, not replacing it. [skill-authoring-explain-the-why-not-musts]

**Behavioral rules:** Express as negative constraints, not positive aspirations. Negative constraints collapse the probability distribution; positive guidance only weakly biases. "Never begin with an apology" is more reliable than "try to be confident." [negative-constraints-as-probabilistic-output-collapse]

**Reasoning-model audit (breaking change):** The following five techniques DEGRADE performance on all three frontier model families (GPT-5.4, Claude 4.6, Gemini 3.1). Audit every skill body and remove them:
- Explicit chain-of-thought ("think step by step")
- Few-shot examples
- Self-consistency runs
- Least-to-most decomposition
- Skeleton-of-thought

Replacement pattern: Goal + Constraints + Context. [reasoning-model-anti-pattern-prescribed-reasoning]

**Interactive vs. scheduled authoring:**
- Interactive skills: outcome-based, declarative format; define success criteria and let the agent explore [declarative-goal-driven-agent-prompting]
- Scheduled / unattended skills: numbered SOP format, named data sources, explicit completion signals, inline edge-case handling [hands-off-routine-prompt-precision-pattern]

Ask "interactive or scheduled?" before choosing a body template. [§3 C7 of master inventory]

---

## 4. Body Sections — Progressive Disclosure (3 Levels)

This three-level architecture is the highest-confidence structural pattern in the research corpus — 6+ independent implementations across BMAD, OpenViking, DeerFlow, Beads, and others. [progressive-tiered-context-loading-convergence]

| Level | Token budget | Content | When loaded |
|-------|-------------|---------|-------------|
| L0 / L1 | ~100 tokens | `name` + `description` from frontmatter | Always, at session start |
| L2 | < 5,000 tokens recommended; ≤ 500 lines hard cap | Full SKILL.md body | On activation / trigger |
| L3+ | Effectively unbounded | Bundled reference files in `references/`, scripts in `scripts/` | On demand, when Claude reads them |
[skill-as-directory-progressive-disclosure-three-levels]

Every authored skill must include all three tiers. [progressive-tiered-context-loading-convergence]

**Context budget mechanics:**
- Skill body enters conversation as one persistent message at activation time; Claude Code does NOT re-read SKILL.md on subsequent turns. [skill-content-lifecycle-context-budget]
- Post-compaction: 5,000 tokens preserved per skill; 25,000 tokens combined budget across all skills; LRU eviction for oldest invocations when over budget. [skill-content-lifecycle-context-budget]
- Critical guidance past 5K tokens is at risk after compaction; most important instructions must be at the top of the body. [skill-content-lifecycle-context-budget]
- Write skills as standing instructions (invariants), not one-time setup steps. [skill-content-lifecycle-context-budget]

**Size evidence:**
- ETH Zurich (438 tasks, 4 agents): context files increase reasoning token usage 14–22%; even human-written files add overhead; LLM-generated files reduce success rates ~3%. [context-file-instruction-bloat-eth-zurich]
- Outcome-based instructions achieve ~50% token reduction vs. procedural instructions. [bmad-outcome-based-skill-rewrite-pattern]
- Brevity constraints improve accuracy 26 percentage points across 31 models. [brevity-constraints-reverse-llm-performance]

**Include an explicit L0 abstract (~100 tokens)** as a named section. Harnesses using progressive loading (DeerFlow, BMAD) inject only this at boot; the full body loads via `read_file` on demand. [progressive-tiered-context-loading-convergence][progressive-skill-loading]

---

## 5. Reference Files — Filesystem Conventions

The canonical skill directory layout:

```
<skill-name>/
  SKILL.md            ← L2 body (≤ 500 lines)
  README.md           ← Human-facing overview (optional)
  references/         ← L3 depth content, loaded on demand
  scripts/            ← Executable utilities (use ${CLAUDE_SKILL_DIR} for paths)
  assets/             ← Static resources: templates, schemas
```
[skill-as-directory-progressive-disclosure-three-levels][skill-as-package-export-with-references]

**Pointers over copies:** SKILL.md should contain only workflow instructions and file path references to shared context — not embedded context copies. Stale context is worse than no context. [pointers-over-copies-in-context-files][skills-as-pointers-to-second-brain-files]

> ETH Zurich finding: agents are "surprisingly good at discovering file structures on their own" — directory listings in SKILL.md don't help and add overhead. [pointers-over-copies-in-context-files]

**Shared context folder pattern:** Domain knowledge that multiple skills reference belongs in a single shared folder; each skill references it by path. Update propagates automatically to all skills on next invocation. [shared-context-folder-as-cross-skill-update-multiplier]

**Hot reload:** SKILL.md text edits take effect immediately in watched directories. New top-level skill directories created mid-session require a session restart. [skill-live-change-detection-hot-reload]

---

## 6. Proposed Additional Fields

These fields are surfaced by findings as necessary for robust cross-AI skill authoring but are not yet in the Claude Code core spec. Authors working with these systems may implement them as conventions until they are standardized.

### 6.1 `specializes` — **proposed**

```yaml
specializes: <core-skill-name>
```

Declares inheritance from a core skill in a shared repository (`common-skills`). Core skills define overridable categories; specialized skills may only customize declared slots without forking the contract (output schema, safety rules, evidence rules). Production-tested at Warp with 15 skills. [core-specialized-skill-inheritance-pattern]

Core skills managed in a separate repo with `skills-lock.json` versioning. [core-specialized-skill-inheritance-pattern]

### 6.2 `rollback_procedure` — **proposed**

```yaml
rollback_procedure: "<path-or-command>"
```

Declares the reversibility audit field for side-effect skills. Required for any skill whose actions are not fully reversible. Supports the reversibility spectrum gate: classify each action on fully reversible → reversible with effort → practically irreversible → irreversible. [agent-action-reversibility-as-design-requirement]

### 6.3 `max_permission_scope` — **proposed**

```yaml
max_permission_scope: "<scope-declaration>"
```

Declares the authority ceiling for delegation chains. Enforces monotonic permission narrowing: each delegation step can only reduce permissions; a sub-skill's scope must be a strict subset of the parent skill's scope. [permission-compounding-across-agent-delegation-chains]

### 6.4 `defaultMode` — **proposed**

```yaml
defaultMode: foreground | background | either
```

Declares the execution mode. Foreground = interactive gate per action. Background = bulk pre-approval at launch, silent deny on unapproved actions. [foreground-vs-background-subagent-permission-models]

### 6.5 Autonomy tier annotation per action — **proposed**

Within the body, every side-effect action must declare its autonomy tier using a 2×2 blast-radius × reversibility matrix:

| Blast radius | Reversible | Irreversible |
|-------------|-----------|--------------|
| Low | Full Autonomy | Proposal-first |
| High | Guarded | Human-required |
[autonomy-gradient-not-binary-delegation]

Criterion: `mutation × (persistent ∨ broad-blast)` → Human-required tier. [advisory-only-for-persistent-mutations]

Persistent mutations of governance docs, schemas, and MCP configs: Human-required regardless of track record. Progressive autonomy applies only within the reversible / low-blast-radius quadrant. [§3 C10 of master inventory]

---

## 7. Field Constraints Table (machine-checkable)

| Field | Hard cap | Char class | Portability | Failure mode |
|-------|----------|-----------|-------------|--------------|
| `name` | 64 chars | `[a-z0-9-]` | Portable | Reserved word (`anthropic`, `claude`) → validation error; XML tag → validation error |
| `description` | 1,024 chars | Any (no XML tags) | Portable | Truncation strips keywords before Claude sees them |
| `description` + `when_to_use` (Claude Code) | 1,536 chars combined | Any (no XML tags) | Harness-specific | Past cap, description truncates; use `/doctor` to diagnose |
| `compatibility` | 500 chars | Any | Portable | None |
| SKILL.md body | 500 lines | Markdown | Portable | Past 5K tokens lost at compaction; past 500 lines Anthropic explicit warning |
| L0 abstract | ~100 tokens | Text | Portable | Missing L0 → skill not compatible with progressive-loading harnesses |
| Bundled script paths | — | `${CLAUDE_SKILL_DIR}/*` | Claude Code | Absolute path breaks on environment migration |
| `disable-model-invocation` | Boolean | `true`/`false` | Harness-specific | `true` removes description from context entirely; `when_to_use` becomes dead text |
| `paths` | — | Glob | Harness-specific | Silent non-trigger on non-matching files |

Sources: [skill-frontmatter-validation-rules][skill-description-budget-context-overflow][skill-as-directory-progressive-disclosure-three-levels][skill-content-lifecycle-context-budget][skill-invocation-control-side-effect-guard][claude-code-skill-frontmatter-extensions]

---

## 8. Validation

### 8.1 Deterministic structural validation

Run before any LLM review:

```bash
skills-ref validate ./my-skill
```

Validates: name character class and length, description bounds, reserved words, XML-tag prohibition. Reports structural correctness only — not description quality. [skill-frontmatter-validation-rules]

**Critical limit:** Deterministic validation cannot catch semantic errors. Structural validity ≠ behavioral correctness. Always follow with empirical eval. [bmad-deterministic-skill-validator]

> "Deterministic rules produce consistent, reproducible results with zero inference cost." [bmad-deterministic-skill-validator]

### 8.2 BMAD-style 19-rule CI validator

For teams, implement a CI validator encoding the following six categories across 19+ rules:
1. Naming conventions
2. Variable usage (`$ARGUMENTS`, `${CLAUDE_SKILL_DIR}`, etc.)
3. Path references (no absolute paths in portable skills)
4. Invocation syntax (`disable-model-invocation` / `user-invocable` flags)
5. Sequence correctness
6. Encapsulation boundaries

> "The rules serve as living documentation of skill file conventions." [bmad-deterministic-skill-validator]

### 8.3 Description optimization loop

Treat triggering as an empirically measurable classification problem:
1. Construct 20 eval queries: 8–10 should-trigger, 8–10 should-not-trigger (near-misses)
2. 60/40 train/test split; run each train query 3 times
3. ≤ 5 iterations; select best description by TEST score (not train score)
4. Command: `python -m scripts.run_loop --eval-set <path> --skill-path <path> --model <id> --max-iterations 5`
[skill-description-optimization-loop-held-out-test]

> "Bad eval queries lead to bad descriptions." Queries must be realistic and specific (file paths, company names, casual speech). "Format this data" is BAD. [skill-description-optimization-loop-held-out-test]

---

*Total: approximately 330 lines. All claims cite a finding. Proposed fields are explicitly tagged.*
