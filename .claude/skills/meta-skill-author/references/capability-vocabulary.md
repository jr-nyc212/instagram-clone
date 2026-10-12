# Capability vocabulary — controlled IDs for capability contracts

Owned by `meta-skill-author` Port mode (§4.0/§4.2). This is the **controlled
vocabulary** for `capability-contract.yaml` sidecars: every capability `id` an
exportable skill declares must come from the list below, so skill contracts
(*requires*) and adapter `## Provides` inventories (*provides*) stay mechanically
matchable at port time. Adding, renaming, or removing an ID is a **gated package
change**: new CHANGELOG entry, and every existing sidecar and adapter Provides table
re-checked against the new list.

## The sidecar schema (`capability-contract.yaml`, schema-version 1)

One file at each **exportable** skill's root, next to SKILL.md — the canonical,
machine-readable form of the skill's capability contract. Three surfaces are
**derived** from it and never hand-maintained separately: the generic port's
capability-contract table, the SKILL.md `compatibility` prose (≤500 chars, built
from the required-tier IDs), and every stage-2 port's "Host capabilities required"
block.

```yaml
schema-version: 1
skill:
  name: <skill-name>            # must equal SKILL.md frontmatter `name`
  version: "<x.y.z>"            # must equal SKILL.md `metadata.version`
capabilities:
  - id: <vocabulary-id>         # kebab-case, from the list below
    tier: required | optional   # required + absent on the host => do not install
    purpose: <one line — what the skill uses it for>
    degradation: <behavior if absent; required-tier may be "inert — do not install without">
    install_hint: <optional — how hosts typically satisfy it>
```

Field naming aligns with the shipped ecosystem shapes this borrows from —
environment-manifest-style `required`/`purpose`/`install_hint`, contract-spec
`recovery` renamed `degradation`, MCPB-style host-compatibility blocks — so the
schema is publication-ready, but it is published nowhere; this workspace is its
only consumer.

**Enforcement is authoring-time only** (validator + workspace audit check the file's
presence and shape). Whether the skill *behaves* as declared is not verified — a
preflight/conformance checker is a known, deliberate gap (the "C upgrade path").

## Capability IDs (v1 — seeded from the four exportable generics' contract tables)

| ID | A host provides this when it offers… |
|---|---|
| `durable-document-store` | A stable, non-dated place to create, read, and update named documents across sessions |
| `internal-document-search` | Queryable search over the host's document corpus (workspace files or indexed org content) |
| `workspace-file-inventory` | Enumeration/read access over a bounded working set of files (workspace, folder, project) |
| `connector-source-discovery` | Enumerable external sources (chat, email, docs platforms) that can be listed and selectively retrieved from, per-source gated |
| `versioned-checkpoints` | Change history with revert over the skill's artifacts (git, built-in version history) |
| `change-detection` | A read-only way to list what changed in the working set this session (diff/status) |
| `script-execution` | Running the skill's bundled deterministic scripts (validators, checkers) and returning output |
| `fresh-context-scoring` | Evaluating/grading in a context separate from the one that drafted (subagent, second session) |
| `human-approval-channel` | Presenting a proposal and receiving explicit per-item human approval before acting |
| `reference-bundle-attachment` | Attaching the skill's reference/template files so they are readable at invocation |
| `byproduct-store` | A designated location for ephemeral tool outputs/caches with a defined cleanup lifecycle |
| `live-web-retrieval` | Search and fetch over public web sources (built-in browsing, search API, or connected external-data tools) |
| `browser-automation` | Driving a live browser page — navigate, inspect, interact — beyond static fetch (peer sampling, UI verification) |
| `image-text-extraction` | Extracting text from images or image-only documents (OCR toolchain or vision-capable model) |
| `generated-media-pipeline` | Generating and downloading derived media artifacts (audio, video, decks) from supplied sources via an external generation service |
| `transcript-archive` | Raw session transcripts readable/copyable into a durable workspace store (episodic memory tier) |
| `copilot-cli-subprocess` | Historical ID for the former GitHub Copilot-specific eval backend; do not add to new sidecars. |
| `agent-cli-subprocess` | Driving a standalone agent CLI as a subprocess — non-interactive prompting, sandbox/permission policy, explicit model attribution, transcript capture — for isolated per-case agent runs. |

## Wiring/activation IDs (v2) — moved (MV23/E20 vocabulary split)

Wiring-scale IDs now live at
`.claude/skills/meta-harness-author/references/wiring-vocabulary.md`, owned by
`meta-harness-author` (the system-scale portability skill). This file remains the
home of **skill-scale** IDs only: sidecars declare v1 IDs; system-contract wiring
rows may declare IDs from either list, and requires × provides matching stays
uniform across both.
