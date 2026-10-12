# Platform Matrix: Skill/Agent Support Across Five AI Platforms

**Purpose:** Side-by-side comparison of skill and agent support across Claude Code, Cursor, GitHub Copilot, OpenAI Codex, and Perplexity. Where findings provide direct evidence, the source finding is cited. Where findings are insufficient, capabilities are marked "Unknown — verify against [platform] docs."

---

## 1. Comparison Matrix

| Capability | Claude Code | Cursor | GitHub Copilot | OpenAI Codex | Perplexity |
|------------|-------------|--------|---------------|--------------|------------|
| **Native skill format** | `SKILL.md` with YAML frontmatter; skills-as-open-portable-standard | Unknown — verify against Cursor docs | Unknown — verify against Copilot docs | `SKILL.md` supported (gstack generates Codex variants) [template-generated-skills-multi-host] | `SKILL.md` used in production; Perplexity cited as early open-standard adopter [skills-as-open-portable-standard] |
| **Auto-load mechanism** | Eager: all descriptions loaded at session start (L1 always in system prompt); body deferred until trigger (lazy) [agent-description-auto-dispatch-routing] | Unknown — verify against Cursor docs | Unknown — verify against Copilot docs | Unknown — verify against Codex docs | Progressive loading: descriptions at boot, full body via read on demand [progressive-skill-loading] |
| **Activation modes** | Trigger-based (description match), always-on (`user-invocable: false`), path-scoped (`paths:`), slash-invocable only (`disable-model-invocation: true`) [skill-invocation-control-side-effect-guard] | Unknown | Unknown | Unknown | Description-based dispatch confirmed [agent-description-auto-dispatch-routing] |
| **Frontmatter standard** | Open standard (6 fields) + ~13 Claude Code extension fields [claude-code-skill-frontmatter-extensions] | Unknown | Unknown | Open standard fields; no Claude Code extensions [template-generated-skills-multi-host] | Open standard fields [skills-as-open-portable-standard] |
| **Tool permissioning** | `allowed-tools` (pre-approve); `disallowed-tools` (block); workspace trust dialog grants silently [claude-code-skill-frontmatter-extensions] | Unknown | Unknown | Unknown | Unknown |
| **Subagent / forked execution** | `context: fork + agent: <type>` spawns isolated subagent; skill body becomes task prompt [skill-forked-subagent-execution] | Unknown | Unknown | Unknown | Subagent dispatch confirmed via description routing [agent-description-auto-dispatch-routing] |
| **Reference file loading** | L3 files in `references/` loaded on demand via bash; scripts in `scripts/` execute without body-context entry [skill-as-directory-progressive-disclosure-three-levels] | Unknown | Unknown | Unknown | Progressive: `read_file` on demand [progressive-skill-loading] |
| **Context-file taxonomy** | `CLAUDE.md` auto-loaded at project level [context-file-taxonomy-claudemd-soulmd-agentsmd] | `.cursorrules` auto-loaded [cross-platform-context-file-strategy] | `AGENTS.md` auto-loaded [context-file-taxonomy-claudemd-soulmd-agentsmd] | `AGENTS.md` (Codex CLI auto-loads) [universal-harness-context-via-symlink] | Unknown — verify against Perplexity docs |
| **HITL approval primitives** | `disable-model-invocation: true` for human-only invocation; auto-mode AI-driven permission classifier; deny-and-continue after 3 consecutive or 20 total denials [claude-code-auto-mode-ai-driven-permission-classif] | Unknown | Unknown | Unknown | Unknown |
| **Verification command** | `skills-ref validate ./my-skill` [skill-frontmatter-validation-rules] | Unknown | Unknown | Unknown | Unknown |
| **Reasoning model availability** | Claude 4.6 Opus with extended thinking [reasoning-model-anti-pattern-prescribed-reasoning] | Unknown | Unknown | GPT-5.4 (frontier reasoning model) [reasoning-model-anti-pattern-prescribed-reasoning] | Unknown |
| **Skill hierarchy / override** | Enterprise > Personal > Project > Plugin (namespaced) [skill-hierarchy-enterprise-personal-project-plugin] | Unknown | Unknown | Unknown | Unknown |
| **Installer templates / adapters** | Native; BMAD generates templates for Claude Code [multi-ide-portability-via-installer-templates] | BMAD generates templates for Cursor variants (Windsurf family) [multi-ide-portability-via-installer-templates] | Unknown | gstack generates Codex variants [template-generated-skills-multi-host] | Unknown |
| **Distribution mechanism** | Plugin marketplace via GitHub repo; `npx skills` CLI; `skills-lock.json` [skill-plugin-marketplace-distribution][skills-lock-portable-agent-skills] | Unknown | Unknown | Unknown | Unknown |

---

## 2. Portable Layer (works everywhere)

The following constitute the guaranteed portable floor. Any skill built exclusively from these elements should operate on any conformant harness. [skills-as-open-portable-standard]

**File naming:**
- File must be named `SKILL.md` (all uppercase) [skill-md-format-yaml-front-matter-requirements]
- Skill must be in a directory whose name matches the `name` field [skill-frontmatter-validation-rules]

**Portable frontmatter fields:**
- `name` — 1–64 chars, `[a-z0-9-]`, no reserved words, no XML [skill-frontmatter-validation-rules]
- `description` — 1–1,024 chars, three-part structure (what + when + capabilities), no XML [skill-description-structure-what-when-capabilities]
- `license` — optional, declare for distributed skills [skill-frontmatter-validation-rules]
- `compatibility` — optional, declare non-portable surface requirements ≤ 500 chars [skill-cross-surface-portability-with-constraints]
- `metadata` — optional key-value map [skill-frontmatter-validation-rules]
- `allowed-tools` — Experimental; optional [skills-as-open-portable-standard]

**Portable body structure:**
- Five-element model (Purpose → Triggering → Instructions → Policies → Output format) [skill-as-new-employee-mental-model]
- Three-level progressive disclosure (L0 abstract ~100 tokens, L2 body ≤ 500 lines, L3 reference files) [skill-as-directory-progressive-disclosure-three-levels]
- `references/` directory for L3 depth content [skill-as-package-export-with-references]
- Pointers over copies — no embedded context copies [pointers-over-copies-in-context-files]

**What does NOT port:**
Any Claude Code extension field (`when_to_use`, `disable-model-invocation`, `user-invocable`, `context: fork`, `agent`, `paths`, `hooks`, `disallowed-tools`, `model`, `effort`, `shell`, body-level `$ARGUMENTS`, dynamic context injection via `` !`cmd` ``). Skills using these fields must declare `compatibility: claude-code`. [claude-code-skill-frontmatter-extensions][skills-as-open-portable-standard]

---

## 3. Per-Platform Adaptation Notes

### 3.1 Claude Code

**What maps directly from open standard:** All six open standard fields; SKILL.md body structure; `references/` directory; progressive disclosure model.

**Claude Code extensions available:** Full ~13-field extension set including `when_to_use`, `disable-model-invocation`, `user-invocable`, `context: fork`, `agent`, `paths`, `hooks`, `allowed-tools`, `disallowed-tools`, `model`, `effort`. [claude-code-skill-frontmatter-extensions]

**Translation required:** None — Claude Code is the reference implementation.

**Context file conventions:** `CLAUDE.md` auto-loaded at project level; skill bodies loaded at activation; compaction budget = 5,000 tokens per skill, 25,000 combined. [skill-content-lifecycle-context-budget]

**Platform-quality note:** ETH Zurich (438 tasks, 4 agents) found Claude Code was the ONLY agent where even human-written context files failed to improve performance. Context files add 14–22% reasoning token overhead. [model-specific-context-file-sensitivity][context-file-instruction-bloat-eth-zurich]

**Distribution:** Plugin marketplace + `npx skills` CLI + `skills-lock.json` + project-level `.claude/skills/` directory [skill-plugin-marketplace-distribution][skills-lock-portable-agent-skills]

### 3.2 Cursor

**What maps directly:** Open standard fields; SKILL.md body structure.

**Translation required:** Cursor uses `.cursorrules` (and likely `.cursor/rules/`) for context injection rather than `CLAUDE.md`. [cross-platform-context-file-strategy]

**What doesn't exist:** Claude Code extension fields (no `disable-model-invocation`, no `context: fork`, no `paths` gating). Verify against Cursor docs before using.

**Adapter strategy:** BMAD maintains installer templates for Cursor-family platforms (Windsurf, Trae, Rovodev, Antigravity) in `tools/installer/ide/templates/`. [multi-ide-portability-via-installer-templates]

> "False portability": skill content is portable but skill effectiveness may depend on platform-specific features not available on all platforms. [multi-ide-portability-via-installer-templates]

### 3.3 GitHub Copilot

**What maps directly:** Open standard fields; SKILL.md body structure.

**Translation required:** Copilot auto-loads `AGENTS.md` (not `CLAUDE.md`). Cross-platform strategy: use symlink (`AGENTS.md -> CLAUDE.md`) for zero-drift dual-harness support, or chain-loader indirection (n8n pattern: root `CLAUDE.md` is a single line `@AGENTS.md`). [context-file-taxonomy-claudemd-soulmd-agentsmd][universal-harness-context-via-symlink][cross-platform-context-file-strategy]

**Context file taxonomy:** `AGENTS.md` = tool-agnostic conventions; Copilot also reads `.github/prompts/` (verify against Copilot docs). [cross-platform-context-file-strategy]

**Symlink caveat:** Windows requires `mklink /D`; tarball/zip distribution may not preserve symlinks. [universal-harness-context-via-symlink]

**What doesn't exist:** Claude Code extension fields; `skills-ref validate` command; plugin marketplace mechanism. Unknown — verify against Copilot docs.

### 3.4 OpenAI Codex

**What maps directly:** Open standard fields; SKILL.md body structure; `references/` directory.

**Evidence:** gstack generates SKILL.md files for 8 platform variants including Codex from `.tmpl` templates. SKILL.md files are build artifacts in this model, not hand-authored. 38 templates produce 41 skills across supported hosts. [template-generated-skills-multi-host]

**Translation required:** Codex CLI auto-loads `AGENTS.md` (not `CLAUDE.md`). Symlink strategy works here. [universal-harness-context-via-symlink]

**Context file taxonomy:** `AGENTS.md` is the auto-loaded file for Codex CLI. [universal-harness-context-via-symlink]

**What doesn't exist:** Claude Code-specific frontmatter extensions; `skills-ref validate`; Claude Code skill hierarchy. Unknown — verify against Codex docs for equivalent mechanisms.

**Reasoning model:** GPT-5.4 is a frontier reasoning model on Codex. Audit skill bodies for prescribed-reasoning anti-patterns (explicit CoT, few-shot, decomposition scaffolding) before deploying — these degrade performance on GPT-5.4. [reasoning-model-anti-pattern-prescribed-reasoning]

### 3.5 Perplexity

**What maps directly:** Open standard fields; SKILL.md body structure; description-based dispatch; progressive loading.

**Evidence:** Perplexity is cited as an early adopter of the open standard; the four-discipline rubric evaluator (`four-discipline-prompt-evaluator`) has been adopted in production at Perplexity. [skills-as-open-portable-standard][four-discipline-prompt-evaluator]

**Auto-load mechanism:** Progressive loading confirmed — descriptions at boot, full SKILL.md body loaded on demand via `read_file` equivalent. [progressive-skill-loading]

**Translation required:** Unknown — verify activation modes, tool permissioning, and frontmatter extension support against Perplexity docs.

**What doesn't exist or is unknown:** Claude Code extension fields; `skills-ref validate` CLI; plugin marketplace. Unknown — verify against Perplexity docs.

---

## 4. Context-File Auto-Load Rules (per harness)

Which file names trigger auto-load in which harness:

| Harness | Auto-loaded file | Notes |
|---------|-----------------|-------|
| Claude Code | `CLAUDE.md` | Project-level; walks up to repo root [context-file-taxonomy-claudemd-soulmd-agentsmd] |
| GitHub Copilot | `AGENTS.md` | Tool-agnostic conventions [context-file-taxonomy-claudemd-soulmd-agentsmd] |
| Cursor | `.cursorrules` | Also reads `.cursor/rules/` — verify against Cursor docs [cross-platform-context-file-strategy] |
| Codex CLI | `AGENTS.md` | Same as Copilot [universal-harness-context-via-symlink] |
| Perplexity | Unknown | Verify against Perplexity docs |

**Cross-harness strategies for maintaining context files:**
1. **Symlink** (`AGENTS.md -> CLAUDE.md`): zero content duplication, zero drift; works on UNIX-like systems; Windows requires `mklink /D`; breaks in tarball distribution [universal-harness-context-via-symlink]
2. **Chain-loader indirection** (n8n pattern): root `CLAUDE.md` is a single line `@AGENTS.md`; note `@` reference is Claude Code-specific syntax [cross-platform-context-file-strategy]
3. **Platform-specific mirroring** (Archon): parallel agent definitions in `.claude/agents/`, `.github/agents/`, `.github/prompts/` — maximum fidelity, highest drift risk [cross-platform-context-file-strategy]
4. **Content duplication** (LangGraph): `CLAUDE.md` and `AGENTS.md` contain identical content — simplest, highest drift risk [cross-platform-context-file-strategy]
5. **Template generation** (gstack): `.tmpl` source generates platform-specific files automatically [template-generated-skills-multi-host]

**ETH Zurich quality constraint (applies to all harnesses):** Manually written, concise context files outperform auto-generated files. LLM-generated context files reduce success rates ~3% and increase inference cost 20%. [context-file-taxonomy-claudemd-soulmd-agentsmd][context-file-instruction-bloat-eth-zurich]

Minimum viable file set per ETH Zurich: `CLAUDE.md` + `SOUL.md` + `system/PROGRESS.md` reduces Day 1 overhead while leaving room to grow. [context-file-taxonomy-claudemd-soulmd-agentsmd]

**OpenClaw SOUL.md stack:** SOUL → tools → memory → skills → overlays; ~20K char cap per layer. [context-file-taxonomy-claudemd-soulmd-agentsmd]

---

## 5. Cross-Surface Compatibility Declaration

Use the `compatibility` field when a skill requires platform-specific features that are not available everywhere. [skill-cross-surface-portability-with-constraints]

```yaml
---
name: my-skill
description: "..."
compatibility: "claude-code"   # Only works on Claude Code; requires filesystem access
---
```

**Surface-specific capability matrix:**

| Surface | Network access | Package install | Sharing model | Beta headers required |
|---------|---------------|----------------|--------------|----------------------|
| claude.ai | Varies by admin policy | N/A | Individual upload | None |
| Claude API | None | Pre-installed packages only | Workspace-shared | `code-execution-2025-08-25`, `skills-2025-10-02`, `files-api-2025-04-14` |
| Claude Code | Full | Local preferred | `.claude/skills/` or plugin | None |
[skill-cross-surface-portability-with-constraints]

Custom skills do NOT sync across surfaces; each deployment is independent. [skill-cross-surface-portability-with-constraints]

**Design guideline:** Design for the most restricted target surface (typically Claude API) and use `compatibility` to declare when a skill expects more. [skill-cross-surface-portability-with-constraints]

**Provider-adaptive rendering:** Letta framework evidence shows Anthropic models respond better to line-numbered memory blocks; GPT uses standard formatting. One prompt format does not work equally well across all models. Consider a rendering adapter layer that applies model-specific formatting without modifying the canonical skill body. [provider-adaptive-prompt-rendering]

---

## 6. Known Gaps and Open Questions

### 6.1 Eager vs. lazy description loading — unresolved across harnesses

Claude Code loads ALL descriptions at session start (eager); body deferred until trigger [agent-description-auto-dispatch-routing]. DeerFlow injects only name+description at boot, then loads full SKILL.md via `read_file` on demand [progressive-skill-loading]. Archon loads only description fields for routing, defers full YAML until after routing [description-based-workflow-routing-lazy-dispatch].

These patterns coexist across different harnesses without a resolved best practice. Design descriptions for BOTH: (a) when loaded eagerly as part of a catalog, the description must earn its context cost; (b) when used as a lazy routing filter, the description must be distinctive enough for correct dispatch without the body. [§3 C4 of master inventory]

### 6.2 Description cap discrepancy — C1

The open standard caps `description` at 1,024 characters [skill-description-structure-what-when-capabilities]. Claude Code's combined `description` + `when_to_use` per-entry cap is 1,536 characters [skill-description-budget-context-overflow]. These govern different fields and are not contradictory. Target ≤ 800 characters for `description` alone to leave room for `when_to_use` on Claude Code. [§3 C1 of master inventory]

### 6.3 Deterministic vs. LLM-based routing — unresolved

Archon's `archon-dev` uses keyword-to-cookbook routing (no AI classification call; faster, more deterministic) [intent-based-meta-routing-skill]. Claude Code uses LLM description-matching [agent-description-auto-dispatch-routing]. BMAD's help system uses LLM classification [bmad-help-adaptive-module-routing].

Resolution: deterministic routing is appropriate when the keyword space is stable and bounded (< 15 skills); LLM description matching is appropriate for large, growing skill libraries where keyword maintenance would be prohibitive. [§3 C5 of master inventory]

### 6.4 Everything-as-skill vs. three-layer chain — architecture-dependent

BMAD v6.2.2 collapsed agents, workflows, and personas into a single SKILL.md primitive [everything-as-skill-architecture]. GSD's three-layer chain (commands → workflows → reference docs) depends on the three-way separation remaining distinct [three-layer-context-chain-loading]. These are "mutually incompatible structural assumptions."

Authors must detect or declare the target harness architecture and emit appropriate output: single unified SKILL.md for BMAD-style targets; three-layer artifact set for GSD-style targets. [§3 C6 of master inventory]

### 6.5 Platform coverage gaps

The following capabilities are unknown for the listed platforms and require verification against current documentation:

- **Cursor:** Activation modes, tool permissioning, subagent execution, HITL primitives, skill hierarchy
- **GitHub Copilot:** Native skill format validation, activation modes, tool permissioning, reasoning model availability
- **OpenAI Codex:** Activation modes, HITL approval primitives, verification command equivalent, distribution mechanism
- **Perplexity:** Context-file auto-load rules, tool permissioning, HITL primitives, verification command

---

*Total: approximately 380 lines. Claims from findings are cited inline. Unknown capabilities are explicitly labeled.*

## 7. Multi-Harness Adapter Pattern Reference

The adapter template pattern is the most concrete portability evidence in the corpus: BMAD maintains installer templates in `tools/installer/ide/templates/` for 7+ platforms — Claude Code, OpenCode, Kiro, Windsurf, Trae, Rovodev, Antigravity. [multi-ide-portability-via-installer-templates]

> "The installer template is a thin adapter layer; the skill is the portable unit." [multi-ide-portability-via-installer-templates]

### 7.1 Adapter template anatomy (MemPalace three-layer model)

MemPalace demonstrates the cleanest implementation of content/packaging separation: [shared-instructions-multi-harness-plugin-wrappers]

```
mempalace/
  instructions/               ← Harness-agnostic instruction source (~1.7k–3.8k bytes each)
    <skill-name>.md
  .claude-plugin/
    commands/<skill>.md       ← Claude Code wrapper (<40 lines; carries frontmatter only)
  .codex-plugin/
    skills/<skill>/SKILL.md   ← Codex wrapper (<40 lines; carries frontmatter only)
  integrations/openclaw/
    SKILL.md                  ← OpenClaw wrapper (<40 lines; carries frontmatter only)
```

Key principle: wrapper files carry only harness-specific packaging metadata (plugin.json, hooks.json, marketplace.json, SKILL frontmatter, MCP registration). They do not carry instruction prose. No instruction content is duplicated across the three harnesses. [shared-instructions-multi-harness-plugin-wrappers]

**Failure mode:** Runtime dependency on the CLI — if the `mempalace` delegation command isn't installed or on PATH when the wrapper runs, delegation fails with a confusing error. [shared-instructions-multi-harness-plugin-wrappers]

### 7.2 Template generation model (gstack)

gstack treats SKILL.md files as build artifacts: `.tmpl` templates are the source of truth; a `gen-skill-docs.ts` build step generates platform-specific SKILL.md files automatically. [template-generated-skills-multi-host]

Host config covers per-platform: preamble content, `allowed-tools`, and tool aliases. 38 templates produce 41 skills across 8 platforms.

**Failure modes:** Manually edited generated files bypass the template (causing drift); build step forgotten after template changes deploys stale SKILL.md. [template-generated-skills-multi-host]

### 7.3 Choosing an adapter strategy

| Situation | Recommended strategy |
|-----------|---------------------|
| Two platforms with identical context-loading mechanism | Symlink (`AGENTS.md -> CLAUDE.md`) [universal-harness-context-via-symlink] |
| Two platforms with different command/skill formats | Plugin wrapper + runtime delegation (MemPalace pattern) [shared-instructions-multi-harness-plugin-wrappers] |
| 3–8 platforms, stable skill schema | Template generation (gstack pattern) [template-generated-skills-multi-host] |
| Small skill count, maximum fidelity per platform | Platform-specific mirroring (Archon pattern) [cross-platform-context-file-strategy] |
| Lowest maintenance, highest drift risk | Content duplication (LangGraph pattern) — not recommended at scale [cross-platform-context-file-strategy] |

**False portability warning:** Skill content is portable but skill effectiveness may depend on platform-specific features (file watching, subagent spawning) not available on all platforms. [multi-ide-portability-via-installer-templates]

---

## 8. Skill Hierarchy and Override Rules (Claude Code)

Claude Code resolves skill names across four tiers with strict override precedence: [skill-hierarchy-enterprise-personal-project-plugin]

```
Enterprise (managed settings)          ← highest priority; overrides all
  └── Personal (~/.claude/skills/)     ← all projects for this user
        └── Project (.claude/skills/)  ← this project only
              └── Plugin (plugin-name:skill-name namespace)
```

Key rules: [skill-hierarchy-enterprise-personal-project-plugin]
- Project skills walk up to repo root — `.claude/skills/` in starting directory AND every parent up to repo root all contribute
- Nested on-demand discovery: working on `packages/frontend/` discovers skills in `packages/frontend/.claude/skills/` (monorepo support)
- Plugin skills use `plugin-name:skill-name` namespace — never collides with unnamespaced tiers
- Skill + command name conflict: skill wins
- **Silent override** is a named failure mode: a project-level skill overrides a personal one without warning

**Enterprise tier:** Shipped December 18, 2025; managed settings enforce enterprise > personal > project precedence. [skill-hierarchy-enterprise-personal-project-plugin]

Other platforms (Cursor, Copilot, Codex, Perplexity): equivalent override hierarchy — Unknown — verify against platform docs.

---

## 9. Capability Evidence Summary by Platform

This section aggregates what the findings directly confirm (as opposed to what is inferred or unknown).

### Confirmed by findings

**Claude Code:**
- SKILL.md as native format — 20 of 29 analyzed repos use this anatomy [skill-anatomy-convergence-20-of-29-repos]
- All 13 extension fields documented and production-shipped [claude-code-skill-frontmatter-extensions]
- Four-tier skill hierarchy in production (Enterprise shipped Dec 18, 2025) [skill-hierarchy-enterprise-personal-project-plugin]
- Context compaction at 5K tokens per skill, 25K total [skill-content-lifecycle-context-budget]
- `skills-ref validate` command exists and enforces open-standard rules [skill-frontmatter-validation-rules]
- Auto-mode AI-driven permission classifier with 93% approval rate / 17% false-negative rate [claude-code-auto-mode-ai-driven-permission-classif]

**BMAD (7+ IDE platforms including Cursor-family):**
- Everything-as-skill architecture collapsed agent/workflow/persona into single SKILL.md [everything-as-skill-architecture]
- 91% package size reduction (533 → 348 files, 6.2MB → 555KB) from migration [skills-as-markdown-sop-files-encode-processes]
- Installer templates in production for 7+ platforms [multi-ide-portability-via-installer-templates]

**gstack (8 platforms including Codex):**
- 38 templates generate 41 skills across Claude, Codex, Cursor, Factory, Kiro, OpenClaw, OpenCode, Slate [template-generated-skills-multi-host]

**Perplexity:**
- Named as early adopter of open standard alongside Google Labs, Vercel, Stripe, Cloudflare, Netlify, Trail of Bits, Sentry, Expo, Hugging Face, Figma [skills-as-open-portable-standard]
- Four-discipline rubric evaluator adopted in production [four-discipline-prompt-evaluator]

### What all platforms should support (open-standard floor)

Any platform claiming conformance with the Agent Skills open standard (agentskills.io) must support: `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools` frontmatter fields; SKILL.md file naming convention; and basic skill activation via description matching. [skills-as-open-portable-standard]

> "Like MCP, we believe skills should be portable across tools and platforms." [skills-as-open-portable-standard]

**Named failure mode:** Vendor extensions becoming the de-facto standard — making the cross-vendor standard nominal. [skills-as-open-portable-standard]

---

*Total: approximately 300+ lines. Claims from findings are cited inline. Unknown capabilities are explicitly labeled.*
