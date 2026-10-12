# Template — Proposal Log (Propose mode output)

> Copy-paste starter for the refresher's Propose mode. Each manifest change entry
> becomes one proposal here, classified and tier-assigned. The proposal log is an
> advisory artifact — Apply mode acts on it only after the required HITL approval
> for each tier `[autonomy-gradient-not-binary-delegation]`.
>
> Store as `proposal-log-YYYYMMDD-HHMM.yaml`, linked to its source manifest.

```yaml
# proposal-log-YYYYMMDD-HHMM.yaml
---
proposal_log_version: "1.0"
run_id: "<same run_id as the source manifest>"
source_manifest_ref: "<path to change-manifest-YYYYMMDD-HHMM.yaml>"
generated_timestamp: "<ISO-8601 datetime with timezone>"

proposals:
  # --- copy this block per proposal; one per addressed manifest change ---
  - id: "<proposal slug, unique within this log>"
    addresses_change_id: "<id from the manifest's changes[] entry>"
    classification: new_concept       # confirms | variant | new_concept | contradicts
    affected_artifact: "references/<file>"   # inventory | SKILL.md | references/<file> | adapters/<file>
    proposed_change: >
      Concrete description of the edit: which section, what is added/reframed/
      removed, and the finding citation that justifies it. No general-knowledge
      justifications — every authoring rule cites a finding.
    justification_finding: "[<finding-filename>]"
    hitl_tier: proposal_first         # guarded | proposal_first | human_required
    one_way_door: false               # true if effectively irreversible once applied
    conflicts_with: []                # ids of other proposals this contradicts
    status: pending                   # pending | approved | rejected | applied | rolled_back

summary:
  total_proposals: 0
  by_classification:
    confirms: 0
    variant: 0
    new_concept: 0
    contradicts: 0
  by_tier:
    guarded: 0
    proposal_first: 0
    human_required: 0
```

## Classification → HITL tier mapping

| Classification | Meaning | Default HITL tier |
|----------------|---------|-------------------|
| `confirms` | Reinforces an existing claim; bump confidence, no semantic change | Guarded (apply + log) |
| `variant` | Reframes an existing claim per new evidence | Proposal-first (human approves) |
| `new_concept` | Introduces a concept not yet in the package | Proposal-first (human approves) |
| `contradicts` | Conflicts with an existing claim | Human-required (refresher cannot proceed alone) |

## Reminders

- The model that drafts proposals must not be the model that runs the regression
  eval — generator-assessor separation is enforced in the pipeline
  `[generator-assessor-separation-in-skill-iteration]`.
- Apply mode runs the 5-step sandbox-first validation pipeline before any live
  file changes `[sandbox-first-modification-validation]`; see
  `helper-meta-skill-author/references/refresh-validation-pipeline.md`.
- Any approved description change re-runs the 20-query optimization loop
  (`templates/eval-query-set.md`) and must not regress the TEST score before
  commit `[skill-description-optimization-loop-held-out-test]`.
