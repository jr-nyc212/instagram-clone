# Template — Change Manifest (Detect mode output)

> Copy-paste starter for the refresher's Detect mode. Full schema and field
> semantics live in `helper-meta-skill-author/references/change-manifest-format.md`
> — that file is the source of truth; this is the blank fill-in form.
>
> A manifest is **Detect output only**: it records what changed, never decides
> what to do (that is Propose mode). Store one YAML file per run, named
> `change-manifest-YYYYMMDD-HHMM.yaml`.

```yaml
# change-manifest-YYYYMMDD-HHMM.yaml
---
manifest_version: "1.0"
run_id: "<uuid-or-deterministic-hash>"
snapshot_timestamp: "<ISO-8601 datetime with timezone>"
baseline_snapshot_ref: "<path-or-hash of the snapshot.yaml compared against>"

sources_checked:
  - source_type: corpus
    source_ref: "<relative path to research corpus directory>"
  - source_type: platform_doc
    source_ref: "<URL or path>"
  # ... one entry per source in source-watchlist.md

run_mode: detect            # fixed value — manifests come only from Detect mode

changes:
  # --- copy this block per detected change; delete if none ---
  - id: "<human-readable slug, unique within this manifest>"
    source_type: corpus               # corpus | platform_doc | package_internal
    source_ref: "<filename, URL, or path of the changed source>"
    change_type: added                # added | removed | modified
    affected_artifact: inventory      # inventory | SKILL.md | references/<file> | adapters/<file>
    brief_description: >
      One or two sentences: what changed and why it may require a package
      update. Enough for a human to triage without reading the full diff.
    raw_diff: null                    # present only for "modified" entries
    content_hash_before: null         # for modified entries
    content_hash_after: "<sha256 or equivalent>"   # for modified/added entries
    addressed_by_proposal_id: null    # null until Propose mode links a proposal

summary:
  total_changes: 0
  by_type:
    added: 0
    removed: 0
    modified: 0
  by_artifact:
    inventory: 0
    "SKILL.md": 0
    "references/*": 0
    "adapters/*": 0
```

## Reminders

- `affected_artifact` strings are exact: `inventory`, `SKILL.md`,
  `references/<filename>`, `adapters/<filename>`.
- A manifest never mutates the package — it is the input to Propose mode, which
  classifies each change as Confirms / Variant / New concept / Contradicts and
  assigns a HITL tier before anything is applied
  `[autonomy-gradient-not-binary-delegation]`.
- Update `findings-master-inventory.md` first; derive all package changes from it
  to prevent snapshot/package drift `[shared-instructions-multi-harness-plugin-wrappers]`.
