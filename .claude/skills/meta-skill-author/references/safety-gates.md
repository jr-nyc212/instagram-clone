# Safety Gates Reference

> Reference doc for the cross-AI skill-authoring meta-skill.
> Every claim cites a finding from the master inventory.

---

## 1. Three Attack Surfaces [skill-security-audit-obligation]

Every skill presents three distinct attack surfaces at install time. Auditors and authors must examine all three channels; missing any one creates a trust gap that the Principle of Lack of Surprise cannot compensate for.

### 1.1 Static Instructions (the SKILL.md body)

The SKILL.md body is **visible at audit time**. A reviewer can read every line before installing. Risks include:

- Instructions that grant broad tool access (`allowed-tools: Bash(*)`) without documented justification — see §5.
- ALL-CAPS imperatives that conceal the reasoning behind a constraint, making it impossible to evaluate intent [skill-authoring-explain-the-why-not-musts].
- Overlapping descriptions between skills that cause the wrong skill to trigger in sensitive contexts [agent-description-auto-dispatch-routing].

**Audit obligation:** Verify that the static body contains only instructions consistent with the skill's stated purpose. A skill's contents **must not surprise the user in their intent if described** — the Principle of Lack of Surprise [skill-security-audit-obligation].

### 1.2 Bundled Scripts (executables, helpers)

Scripts shipped alongside SKILL.md are **visible but harder to evaluate** than prose instructions. Risks include:

- Shell scripts that escalate privileges or reach outside declared paths.
- Dynamic script generation at runtime that was not present at review.
- Code that makes network calls not declared in the frontmatter tool list.

**Audit obligation:** For every bundled script, enumerate all side effects, verify no undeclared resource access, and confirm the script is scoped to the minimum required operations [tiered-permission-system-bash-safety].

### 1.3 Dynamic External Content (web fetches, MCP tool output)

Dynamic content fetched at runtime is **NOT visible at audit time**. A URL that served benign content during review can serve malicious content later [skill-security-audit-obligation]. This is the highest-risk channel.

Risks include:

- URL-fetched instructions that override the static body after deployment.
- MCP tool descriptions that carry prompt injection payloads — **tool poisoning attacks** [mcp-tool-description-prompt-injection-attack]. MCP tool descriptions are model-readable metadata entering agent context as part of tool discovery; they are a live injection surface.
- Stale data from one external system silently contaminating fresh data from another [cross-system-permission-composition-audit-gap].

**Audit obligation:** Every external URL or MCP server connection must be declared in the frontmatter. Skills that fetch external content at runtime must classify that content as **untrusted** and apply the five-layer prompt architecture's trust classification to retrieved data [five-layer-agent-prompt-architecture].

### 1.4 Trust Boundary at Install Time

The trust decision occurs **at install time**, not at runtime. Once installed, the skill inherits the trust level of its tier:

- Built-in (highest trust, always available)
- Plug-in (medium trust, disableable)
- User-defined / skill-author (lowest trust) [tiered-permission-system-bash-safety]

Skills should be designed as though they will be audited by a cautious reviewer who has never seen the underlying domain. The install-time contract is the only assurance the user has before execution begins.

### 1.5 Principle of Lack of Surprise

> "A skill's contents should not surprise the user in their intent if described." [skill-security-audit-obligation]

This principle is the audit criterion that unifies the three attack surfaces. If reading the static instructions, bundled scripts, and declared dynamic sources together leaves an auditor surprised by what the skill can reach or do, the skill fails the trust boundary check.

---

## 2. Autonomy Gradient (Four Levels) [autonomy-gradient-not-binary-delegation]

Autonomy is not binary. Assigning a skill either "full autonomy" or "needs human approval" collapses a spectrum that has four distinct operational modes. The four levels must be assigned **per decision type**, not blanket across the skill.

### 2.1 The Four Levels

| Level | Name | Behavior |
|-------|------|----------|
| 1 | **Full Autonomy** | Act; no notification required |
| 2 | **Guarded** | Act, then report what was done |
| 3 | **Proposal-first** | Propose the full intended plan; wait for approval before any action |
| 4 | **Human-required** | Escalate; cannot act |

Anthropic's Plan Mode is the production implementation of Proposal-first (Level 3): the agent shows its full intended plan upfront for review, edit, and approval before executing any action [autonomy-gradient-not-binary-delegation].

`dangerously-skip-permissions` (equivalent to collapsing all decisions to Level 1) creates real security and reliability failures by day 30 even if it appears faster on day one [autonomy-gradient-not-binary-delegation].

### 2.2 Assignment via 2×2 Matrix

Autonomy tier is assigned using a matrix of **blast radius × reversibility** [autonomy-gradient-not-binary-delegation]:

```
                    REVERSIBLE          IRREVERSIBLE
                 ┌────────────────┬────────────────────┐
LOW BLAST RADIUS │ Full Autonomy  │     Guarded        │
                 ├────────────────┼────────────────────┤
HIGH BLAST RADIUS│ Proposal-first │   Human-required   │
                 └────────────────┴────────────────────┘
```

- **Low blast radius + reversible** → Full Autonomy (read-only queries, draft generation, local file edits with version control)
- **Low blast radius + irreversible** → Guarded (act then report)
- **High blast radius + reversible** → Proposal-first (show plan, wait for approval)
- **High blast radius + irreversible** → Human-required (escalate; do not act)

The additional criterion for Human-required: `mutation × (persistent ∨ broad-blast)` — any mutation of state that is either persistent (survives beyond the current session) or broadly-scoped (affects more than the immediate task) must be Human-required [advisory-only-for-persistent-mutations].

### 2.3 Per-Decision-Type Assignment (Not Blanket)

A single skill may contain actions at different autonomy levels. Assign a tier to **each action type**, not to the skill as a whole. Example for a skill that manages both research and publishing:

- Read external web page → Full Autonomy
- Draft a local report file → Full Autonomy
- Update a shared governance doc → Proposal-first
- Send a published communication → Human-required

This prevents the common failure mode of granting the highest-required tier to all actions, which creates unnecessary friction on low-risk steps [autonomy-gradient-not-binary-delegation].

---

## 3. The 16 HITL Primitives (Full Catalog) [extract-B5_safety_hitl]

The following 16 primitives are each applicable to different skill types and contexts. A meta-skill generating skills must declare which primitives apply to which actions. Source: all 17 findings in B5, summarized in §2.7 of the master inventory [findings-master-inventory].

---

### Primitive 1: Advisory-Only Gate [advisory-only-for-persistent-mutations]

**When used:** Any action that would mutate persistent or broadly-scoped state (database schema changes, governance doc mutations, MCP server registrations, cross-system config).

**Format at gate:** The system surfaces a structured recommendation artifact — not an applied change. The maintainer-facing contract has five explicit steps:
1. System recommends (with rollback command included)
2. Human inspects the recommendation
3. Human applies the change
4. Human records the change
5. Human reverses if needed

Silent mutation of broadly-scoped persistent state is categorically different from silent mutation of ephemeral state and must never be delegated to the agent.

---

### Primitive 2: Four-Level Autonomy Gradient [autonomy-gradient-not-binary-delegation]

**When used:** Every skill action; replaces global approval policy.

**Format at gate:** Per-decision-type tier assignment embedded in the skill's frontmatter metadata. Anthropic's Plan Mode implements the Proposal-first tier with a structured plan display before execution. Misclassification of blast radius is the primary failure mode; agents may not detect when a decision's blast radius has changed.

---

### Primitive 3: Reasoning-Blind Transcript Classifier [claude-code-auto-mode-ai-driven-permission-classif]

**When used:** Automated classification of proposed actions before execution; used when full human approval is too slow but full autonomy is too risky.

**Format at gate:** A secondary AI model (Claude Code: Sonnet 4.6) evaluates every proposed action using **only** user messages and tool calls — never the agent's own reasoning chain. The classifier is reasoning-blind by design: the agent cannot justify its way past a safety gate. Anthropic published a 17% false-negative rate on overeager actions for this classifier.

---

### Primitive 4: Deny-and-Continue [claude-code-auto-mode-ai-driven-permission-classif]

**When used:** When a proposed action is blocked by the classifier or approval gate but the agent should find an alternative path rather than hard-failing.

**Format at gate:** Blocked actions return as tool results with instructions to find safer paths. After 3 consecutive denials or 20 total denials, escalates to human. In headless mode, terminates. This avoids the failure mode of a blocked action causing the entire workflow to abort.

---

### Primitive 5: Reversibility Spectrum Gate [agent-action-reversibility-as-design-requirement]

**When used:** Applied at design time to classify every action a skill will take; governs how aggressive the runtime gate must be.

**Four-point reversibility spectrum:**
1. **Fully reversible** — read-only queries, draft generation, local file edits with version control → minimal gate
2. **Reversible with effort** — changes to shared documents, database writes with backups → guarded
3. **Practically irreversible** — sent communications, triggered payments, published content, deleted data without backup → human approval required before action
4. **Irreversible** — legal commitments, regulatory filings, physical-world actions → **must not be delegatable to agents at all**

Reversibility is infrastructure-dependent, not action-intrinsic: a database write is reversible if tested restore procedures exist; the same write is irreversible without them [agent-action-reversibility-as-design-requirement].

---

### Primitive 6: Foreground Pass-Through / Background Pre-Approval [foreground-vs-background-subagent-permission-models]

**When used:** Execution mode selection for subagents.

**Format at gate:**
- **Foreground (default):** Blocks main conversation until complete; every permission prompt and clarifying question passes through to the user in real-time. Appropriate for destructive-operation skills.
- **Background:** All tool permissions are requested upfront before launch; once running, the subagent auto-denies anything not pre-approved; clarifying questions fail mid-execution. Appropriate for strictly read-only skills.

Skills that require interactive clarification are incompatible with background mode unless `requires: foreground | either` is declared in skill metadata [foreground-vs-background-subagent-permission-models].

---

### Primitive 7: Mandatory Phase-Boundary UAT [mandatory-user-acceptance-testing-uat-at-phase-bo]

**When used:** At every build phase boundary before proceeding to the next phase.

**Format at gate:** Human must run and confirm that built functionality works end-to-end (API calls, UI flows, integrations). File creation is **explicitly disqualified** as a completion signal. Rubber-stamping the UAT without genuinely testing reduces the safety gate to theater.

---

### Primitive 8: Red-Verification Step (Confirm Failure First) [confirm-failure-first-tdd-agent-discipline]

**When used:** In agent-driven TDD, between writing a test and implementing the code to pass it.

**Format at gate:** Agent must:
1. Run the new test
2. Observe it fail
3. Log the specific failure message (not just exit code) as a logged artifact

Only then proceed to implementation. A test that passes on first run was either malformed (matching existing behavior) or testing nothing. Classical TDD assumes a human would notice; agents follow the recipe literally and do not reliably detect this [confirm-failure-first-tdd-agent-discipline].

---

### Primitive 9: Veto Protocol (Pause Points with Decision Summary) [human-on-the-loop-hotl-autonomy-tiering-framework]

**When used:** At standardized pause points before consequential agent actions.

**Format at gate:** The agent outputs a three-question Decision Summary:
1. **What action am I taking?**
2. **Why is this the optimal path?** (the Logic Chain)
3. **What is the projected impact?**

The human then approves or vetoes. EU AI Act Article 14 requires demonstrable human oversight, making Veto Protocol documentation non-optional for regulated deployments [human-on-the-loop-hotl-autonomy-tiering-framework].

---

### Primitive 10: Algorithmic Guardrails (Threshold-Not-Procedure) [human-on-the-loop-hotl-autonomy-tiering-framework]

**When used:** Encoding behavioral constraints in skills where the agent should operate autonomously within a defined scope.

**Format at gate:** Express constraints as explicit numeric or scope thresholds, not procedural descriptions. Example: "The agent may reallocate budget between marketing channels autonomously, provided the shift does not exceed $5,000 per day" — not "the agent should be careful about large budget changes."

The agent operates autonomously within the threshold and pauses when it would cross it. Procedural descriptions require the agent to infer the threshold; explicit numbers are unambiguous.

---

### Primitive 11: Interrupt / Command Resumption [interrupt-command-primitives-human-in-the-loop]

**When used:** Workflow graphs (LangGraph-style) that need to pause mid-execution for human review.

**Format at gate:** `interrupt(value)` pauses graph execution at any node; full state is checkpointed (persists for hours without timeout). Human responds with `Command(goto="node_name", update={"key": "value"})` combining state mutation and routing in one atomic primitive.

**Four human response modes:**
1. Approve and continue (`goto=next_node`)
2. Reject and redirect (`goto=different_node`)
3. Modify state and continue (`update={...}`)
4. Ask agent to reconsider (`goto=same_node, update={feedback}`)

Binary approval gates are simpler but cannot capture the richness of real human-agent collaboration [interrupt-command-primitives-human-in-the-loop].

---

### Primitive 12: Explicit Resource Allow-Listing [explicit-permission-allow-listing-for-agent-resou]

**When used:** Every time a skill tries to access a resource not already pre-authorized.

**Format at gate:** A permission prompt appears before the task proceeds (modeled on mobile OS permission dialogs). The allow-list is auditable and persistent per skill. Every novel resource access — file path, API endpoint, system service — requires explicit approval before proceeding.

Permission fatigue is the primary failure mode: if every skill triggers multiple approval dialogs, users may start blindly approving. Proposed mitigation: persistent allow-lists per skill to reduce repeat dialogs; permission groupings by trust level (read-only, read-write, execute) [explicit-permission-allow-listing-for-agent-resou].

---

### Primitive 13: Progressive Autonomy Ramp with Trust Ledger [trust-calibration-progressive-autonomy-ramp]

**When used:** Per-task-type trust accumulation over time, allowing tier promotion without manual configuration.

**Format at gate:** A lightweight trust ledger tracks success/failure rates per skill or task type. Once a threshold is reached (e.g., 20 consecutive successful research-loop runs), the human gate shifts from approval-required to spot-check. Trust is **per-task-type**, not global: good skill-generation track record does not justify raising autonomy on governance-doc mutation.

Regression risk: an agent update could invalidate previously earned trust without the system detecting the change [trust-calibration-progressive-autonomy-ramp].

**Hard constraint from C10:** A skill with a perfect track record **cannot** be promoted past the "advisory-only" tier for schema mutations, governance doc changes, or irreversible actions. Progressive autonomy applies only within the reversible/low-blast-radius quadrant [advisory-only-for-persistent-mutations].

---

### Primitive 14: Permission Manifest (Pre-Deployment Cross-System Audit) [cross-system-permission-composition-audit-gap]

**When used:** Before any multi-system agent workflow ships.

**Format at gate:** A permission manifest declaring all systems the workflow will touch is reviewed and approved before deployment. Cross-system correlation IDs (unique trace ID per agent run, passed to every system touched) are then attached for post-hoc audit trail composition.

When an agent crosses multiple independently-governed systems in a single workflow, no individual system evaluates the legitimacy of the composite access. The composite of legitimate per-system accesses can violate a policy no individual system knows about [cross-system-permission-composition-audit-gap].

---

### Primitive 15: Monotonic Permission Narrowing [permission-compounding-across-agent-delegation-chains]

**When used:** Every agent delegation step in multi-agent or multi-skill workflows.

**Format at gate:** Each delegation step can **only reduce** permissions, never expand them. Agent B's permission scope must be a strict subset of Agent A's delegated scope. Authority ceilings (maximum scope caps) enforce this as a hard invariant — encoded as `max_permission_scope` in the skill schema.

Three compounding patterns that this primitive blocks:
- **Inheritance:** Agent B inherits Agent A's full credential scope even though B's task requires only a subset
- **Escalation:** A can read client data + B can write to production → delegated B effectively has read+write, which neither held alone
- **Intersection gap:** No system checks the composite of legitimate per-system accesses [permission-compounding-across-agent-delegation-chains]

---

### Primitive 16: Output-Format-as-Gate [html-output-as-human-in-the-loop-restorer]

**When used:** Any decision point where a human must review agent output before approval.

**Format at gate:** Output format is a **governance decision**, not an aesthetic one. A format the human will not read is functionally equivalent to no gate at all. HTML is prescribed over Markdown walls of text for decision-point outputs because HTML is navigable, visually organized, and engaging enough that the human actually opens, clicks, and suggests changes.

> "Output format is not cosmetic — it is a governance mechanism." [html-output-as-human-in-the-loop-restorer]

93% of users approve prompts without close attention (Anthropic published data), meaning Markdown dumps at approval gates are de-facto rubber stamps [claude-code-auto-mode-ai-driven-permission-classif].

---

## 4. Output Format at Gates

### 4.1 Structured Proposal Format (Proposal-First / Level 3)

When a skill operates at Level 3 (Proposal-first), the agent presents a structured proposal before any action. Minimum required fields:

```
PROPOSED ACTION
───────────────
Action:         [What will be done]
Affected scope: [Which files, systems, records, or users]
Reversibility:  [Fully reversible | Reversible with effort | Practically irreversible | Irreversible]
Rollback:       [Procedure to undo if needed; or "No rollback available"]
Why optimal:    [The Logic Chain — why this path was chosen over alternatives]
Projected impact: [What will change if this proceeds]

APPROVE? (yes / no / modify)
```

This format is derived from the Veto Protocol's three-question Decision Summary [human-on-the-loop-hotl-autonomy-tiering-framework], extended with reversibility and rollback fields required by [agent-action-reversibility-as-design-requirement].

### 4.2 Confirmation Requirements by Level

| Level | Confirmation requirement |
|-------|-------------------------|
| Full Autonomy | None |
| Guarded | Post-action summary; no pre-approval |
| Proposal-first | Structured proposal (§4.1); must receive explicit approval before proceeding |
| Human-required | Escalation artifact only; no action until human initiates |
| Advisory-only (mutations) | Recommendation artifact with rollback command; human applies manually |

---

## 5. Permission Declaration in Frontmatter [claude-code-skill-frontmatter-extensions]

### 5.1 allowed-tools / disallowed-tools

```yaml
allowed-tools: Read, Write, Bash(git log*), Bash(python*)
disallowed-tools: Bash(rm*), Bash(curl*), WebSearch
```

- `allowed-tools` pre-approves tools without per-invocation prompting; the trust dialog grants authority **silently** — authors must not over-specify [claude-code-skill-frontmatter-extensions].
- `disallowed-tools` explicitly blocks tools even if the parent environment grants them.
- **Audit obligation:** A skill with `allowed-tools: Bash(*)` checked into a project grants itself broad authority after the workspace trust dialog. This is the **allowed-tools grant inflation** anti-pattern [skill-security-audit-obligation].

### 5.2 Paths Gating [claude-code-skill-frontmatter-extensions]

```yaml
paths: ["src/**/*.ts", "tests/**/*.spec.ts"]
```

The `paths` field gates auto-load to specific file-glob patterns. Skills without `paths` load in any file context, potentially triggering on unrelated files. Skills silently will not auto-load when the current file does not match the glob — authors must test both the positive and negative case [claude-code-skill-frontmatter-extensions].

### 5.3 disable-model-invocation for Side-Effect Skills [skill-invocation-control-side-effect-guard]

```yaml
disable-model-invocation: true
```

When `disable-model-invocation: true`:
- Claude **cannot** auto-load this skill; the description is NOT in context.
- The skill is only invocable via explicit slash command.
- Use for side-effect skills: commit, deploy, send-slack, publish.
- This prevents the skill from triggering autonomously during a workflow where only a read operation was intended [skill-invocation-control-side-effect-guard].

### 5.4 user-invocable: false Semantics [skill-invocation-control-side-effect-guard]

```yaml
user-invocable: false
```

When `user-invocable: false`:
- The user **cannot** invoke this skill via slash command.
- Claude **can** load it; the description IS in context.
- Use for background knowledge skills that should be available to Claude but not surfaced to the user as a command option.
- Distinct from `disable-model-invocation`; the two fields control different invocation channels independently.

---

## 6. Reversibility & Rollback [agent-action-reversibility-as-design-requirement]

### 6.1 rollback_procedure as Design Requirement

Every skill that mutates state must include a `rollback_procedure` field in its definition. This is a schema requirement, not optional documentation [agent-action-reversibility-as-design-requirement].

Example:
```yaml
rollback_procedure: >
  git revert HEAD~1 to undo the last commit;
  run `db restore --backup latest` to restore the database snapshot
  taken immediately before this skill was invoked.
```

If no rollback procedure exists, the action is **practically irreversible by default** and must be gated at Human-required regardless of the blast radius matrix assignment.

### 6.2 Reversibility vs. Irreversibility: The Infrastructure Dependency

Reversibility is not intrinsic to the action — it depends on the infrastructure around it [agent-action-reversibility-as-design-requirement]:

| Action | Reversible (with) | Irreversible (without) |
|--------|-------------------|------------------------|
| Database write | Tested restore procedure + recent backup | No backup or untested restore |
| File delete | Version control with clean history | No version control |
| Email send | Draft-only mode enforced by skill | Sent directly |
| Config change | Snapshot taken before change | No snapshot |

When infrastructure changes (e.g., backup schedule shifts from hourly to weekly), reversibility classification must be re-evaluated. Skills should embed the infrastructure dependency explicitly in the `rollback_procedure` field.

### 6.3 The Lilly Incident Precedent

An agent with production write access could have silently rewritten system prompts governing AI advisory logic — an action practically irreversible because detection requires comparing against known-good baselines that may not exist [agent-action-reversibility-as-design-requirement]. This incident is the canonical justification for treating all production-write actions as requiring explicit reversibility classification before deployment.

---

## 7. Permission Compounding [permission-compounding-across-agent-delegation-chains]

### 7.1 max_permission_scope as Ceiling

Every skill that spawns sub-skills or delegates to specialist agents must declare a `max_permission_scope` field. This is the authority ceiling: no downstream agent in the delegation chain can exceed this scope regardless of what the downstream agent's own configuration declares [permission-compounding-across-agent-delegation-chains].

```yaml
max_permission_scope: "read-only:src/, write:reports/"
```

### 7.2 Delegation Chain Risk

The compound permission surface grows combinatorially with each delegation step. Human delegation naturally bounds this through screen-mediated access; agent delegation has no such implicit bound [permission-compounding-across-agent-delegation-chains].

The three compounding patterns (inheritance, escalation, intersection gap) each produce a different failure mode:

- **Inheritance risk:** Sub-skill inherits broad research permissions from parent and uses them to write production config.
- **Escalation risk:** Skill A can read client data; Skill B can write to external services; the delegation gives Skill B read+write capability that neither declared independently.
- **Intersection gap:** Each system grants access independently; the composite access violates a policy no individual system was aware of.

**Required pre-deployment check:** Enumerate all systems touched by the full delegation chain and verify the composite access is intentional. This compound permission audit must be a pre-deployment gate for multi-agent workflows.

### 7.3 Monotonic Narrowing Enforcement

Each delegation step must narrow the permission scope:

```
Meta-skill scope: {read:*, write:reports/, bash:git}
  └─ Sub-skill A scope: {read:src/, write:reports/}   ✓ (strict subset)
       └─ Sub-skill B scope: {read:src/}               ✓ (strict subset)
  └─ Sub-skill C scope: {read:*, write:*, bash:*}      ✗ VIOLATION
```

Sub-skill C would violate monotonic narrowing; the meta-skill must block this delegation.

---

## 8. Prompt Injection Defenses

### 8.1 MCP Tool Description Poisoning [mcp-tool-description-prompt-injection-attack]

MCP tool descriptions are model-readable metadata that enter agent context during tool discovery. This makes them a **live prompt injection surface** — "tool poisoning attacks." An adversarial MCP server can embed instructions in tool descriptions that the agent executes as if they came from the skill author.

**Defenses:**
- Treat every MCP tool description as untrusted content until verified [tool-access-as-security-boundary-not-feature-toggle].
- Do not connect MCP servers whose capabilities exceed what the agent needs — per-call approval is defense-in-depth; the primary defense is scope restriction.
- Claude Code Auto Mode inserts a prompt injection probe on **all tool output** before it enters Claude's context [claude-code-auto-mode-ai-driven-permission-classif].

### 8.2 Trusted vs. Untrusted Content Classification [five-layer-agent-prompt-architecture]

The five-layer agent prompt architecture requires explicit trust classification on all retrieved data in Layer 3 (Context & Retrieved Data):

| Content source | Trust level | Handling |
|----------------|-------------|---------|
| Skill body (SKILL.md) | Trusted (audited at install) | Execute as instructions |
| User messages | Trusted (direct from user) | Execute as instructions |
| MCP tool output | **Untrusted** by default | Sanitize; do not execute as instructions |
| Web fetches | **Untrusted** | Sanitize; do not execute as instructions |
| Retrieved documents | Depends on source | Verify provenance before trust elevation |

Failing to classify retrieved content as untrusted is the root cause of most prompt injection successes in agentic systems [five-layer-agent-prompt-architecture].

### 8.3 Frontmatter Character-Class Restrictions [skill-md-frontmatter-as-discovery-trigger-primitive]

Frontmatter restrictions are prompt injection defenses, not style rules:

- **No XML angle brackets** (`<`, `>`) in name or description fields — limits injection vectors.
- **No reserved words** (`anthropic`, `claude`) in the name field — prevents impersonation of trusted system skills.
- **Non-empty description** — empty descriptions create undefined dispatch behavior.

These restrictions are validated mechanically via `skills-ref validate` [skill-frontmatter-validation-rules]. The frontmatter enters Claude's system prompt at startup; any injection payload in the frontmatter executes at session initialization, before any user interaction [skill-md-frontmatter-as-discovery-trigger-primitive].

---

## Summary Table: Gate Selection by Action Type

| Action type | Reversibility | Blast radius | Required tier | Required primitive(s) |
|-------------|--------------|--------------|---------------|-----------------------|
| Read-only file access | Fully reversible | Low | Full Autonomy | Explicit resource allow-listing |
| Local file write (version-controlled) | Fully reversible | Low | Full Autonomy | Rollback procedure documented |
| Shared document update | Reversible with effort | Medium | Proposal-first | Structured proposal + Reversibility gate |
| Schema / config change | Reversible with effort | High | Proposal-first or Human-required | Advisory-only gate + Rollback procedure |
| Sent communication | Practically irreversible | Medium | Human-required | Veto Protocol + Confirmation |
| Governance doc mutation | Practically irreversible | High | Human-required + Advisory-only | Permission manifest + Proposal |
| Legal/regulatory filing | Irreversible | High | Not delegatable | N/A — remove from skill scope |
| Multi-system workflow | Varies | High | Permission manifest required | Cross-system audit + Monotonic narrowing |
| Sub-skill delegation | Inherited | Inherited | max_permission_scope ceiling | Monotonic narrowing |
