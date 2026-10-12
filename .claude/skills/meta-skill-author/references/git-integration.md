# Git Integration: Versioning, CI, and Distribution

**Purpose:** How to put a skill under version control, gate it in CI, and distribute it across teams and platforms. A skill is the `package.json` of agent capabilities — it should live in the same repo as the code it governs, move through the same review pipeline, and version with the same discipline [project-specific-custom-skills-for-repeated-task]. This doc covers the lifecycle from first commit to multi-team distribution. It is platform-portable: nothing here depends on a single harness.

---

## 1. Treat the skill as a versioned policy artifact

A skill is not freeform prose; it is policy. Version it like one. The prompt-as-policy model gives every skill four explicit properties that map cleanly onto version-controlled artifacts: **ROLE**, **AUTHORITY**, **CONSTRAINT**, and **FAILURE SIGNAL** — and hooks those properties into CI/CD [prompt-as-policy-version-control-and-cicd-for-agen].

What this means in practice:

- The skill body and its `references/` live in the repo, not in a personal scratch folder.
- Changes go through pull request review, not direct edits to a deployed copy.
- A change to a published rule's meaning is a reviewable diff, not an invisible behavioral drift.

> Treating agent prompts as versioned policy artifacts with ROLE / AUTHORITY / CONSTRAINT / FAILURE SIGNAL properties and CI/CD hooks formalizes skill versioning. [prompt-as-policy-version-control-and-cicd-for-agen]

---

## 2. Repository layout

Co-locate the skill with the code it governs. The promotion step in the authoring sequence is explicit about this: once a skill passes its trigger and near-miss gates, add it to version control alongside the code, not in a separate "prompts" island [project-specific-custom-skills-for-repeated-task].

```
repo/
├─ src/...                      # the code the skill governs
├─ skills/
│  └─ my-skill/
│     ├─ SKILL.md               # body ≤ 500 lines
│     ├─ references/            # pointers, not copies
│     ├─ scripts/validate.sh    # the deterministic gate (this package)
│     └─ CHANGELOG.md           # human-readable version history
└─ skills-lock.json             # team: pinned skill versions
```

For monorepos, choose one of three documented context-distribution strategies and apply it consistently — do not mix them within one repo [monorepo-context-distribution-three-strategies]:

| Strategy | When to use |
|----------|-------------|
| Single root context file | Small repo, one team, shared conventions |
| Per-package context files | Independent packages with divergent conventions |
| Root + per-package overrides | Shared baseline with local specialization |

Use **pointers over copies** between these files — duplicated context across the tree is the same bloat anti-pattern in distributed form [pointers-over-copies-in-context-files].

---

## 3. Semantic versioning for skills

This package's `CHANGELOG.md` defines the bump rules; reuse them for any skill:

| Change | Bump |
|--------|------|
| A foundational finding changes meaning | **minor** at minimum |
| A published rule's meaning changes | **minor** |
| New reference / example / template added (no rule change) | **minor** |
| Prose tightening, typo fixes, formatting | **patch** |
| Breaking restructure of package layout | **major** |

The changelog is a **user-facing surface**, not bookkeeping: a consumer reads it to learn whether they are running a stale snapshot of the underlying research corpus. Keep it human-readable and derive it from the refresher's internal audit-log entries when one exists.

---

## 4. CI gate: run the deterministic validator on every change

Wire `scripts/validate.sh` into the pipeline so no skill merges while structurally broken. The validator is built for exactly this: no network, no platform tooling, exit `0` = PASS (warnings allowed), `1` = FAIL, `2` = usage error [bmad-deterministic-skill-validator].

Minimal CI step (GitHub Actions shown; portable to any runner):

```yaml
# .github/workflows/skills.yml
name: validate-skills
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate every skill
        run: |
          set -e
          for d in skills/*/; do
            echo "::group::$d"
            bash "$d/scripts/validate.sh" "$d"   # exit 1 fails the job
            echo "::endgroup::"
          done
```

Level 1 is necessary but **not sufficient** — it catches structural defects, not behavioral ones. A passing validator must still be followed by the Level 2 audit in a *separate Grader context*, never the author's [generator-assessor-separation-in-skill-iteration]. Treat the four-discipline rubric and capability evals as the behavioral gate that runs after the structural one [four-discipline-prompt-evaluator].

Map the FAILURE SIGNAL property to the CI exit code: a non-zero validator exit is the policy's own declared failure signal, surfaced where reviewers see it [prompt-as-policy-version-control-and-cicd-for-agen].

---

## 5. Branch & review discipline

- **One logical change per PR.** Run the eval harness after each change; do not batch unrelated edits into one diff [claude-code-skills-20-four-mode-skill-lifecycle-wi].
- **Sandbox-first.** Validate proposed modifications in isolation before merging. Evidence: 78–92% of proposed modifications maintain or improve performance, forced rollbacks run 8–22%, and undetected regressions stay under 1% with proper sandbox-first governance [sandbox-first-modification-validation].
- **Blind review for behavior.** The reviewer who runs the behavioral eval should not be the author and should not see the authoring rationale — sycophancy in self-review is systemic [generator-assessor-separation-in-skill-iteration].
- **Capability evals graduate.** When a capability eval consistently passes, move it into the committed regression suite so future PRs can't silently break it [capability-vs-regression-eval-lifecycle].

---

## 6. Distribution

How a skill leaves your repo depends on audience.

| Audience | Mechanism | Notes |
|----------|-----------|-------|
| Single repo / single team | Commit in `skills/`, pin in `skills-lock.json` | Simplest; version travels with the code [project-specific-custom-skills-for-repeated-task] |
| Multiple repos / one org | Plugin / marketplace distribution | Publish the skill as an installable unit; consumers pull a pinned version [skill-plugin-marketplace-distribution] |
| Cross-platform (the 5 targets) | Installer templates from a portable core | Keep one canonical instruction layer; generate thin per-platform wrappers [multi-ide-portability-via-installer-templates] |
| Workflows reused across projects | Register-and-run portability | Register the workflow once, invoke by description from any project [cross-project-workflow-portability-register-and-run] |

For cross-platform distribution specifically, do **not** fork the body per platform. Separate the canonical instruction content from harness-specific packaging and ship multi-harness wrappers around the same core — this is the Port-mode discipline and it is what keeps versions from diverging [shared-instructions-multi-harness-plugin-wrappers]. See `SKILL.md` §4 and the `adapters/` directory for the per-platform wrapper details.

When the skill self-improves in the field, append a Lessons Log to the body and version those lessons too — they are part of the artifact's history, asking after each invocation: lost work? reasonable tokens? user correction? [self-improving-skill-lessons-log]

---

## 7. Quick checklist

- [ ] Skill lives in the repo beside the code it governs, not a personal folder.
- [ ] `validate.sh` runs in CI and fails the build on exit ≠ 0.
- [ ] Behavioral audit (Level 2) runs in a separate context after Level 1 passes.
- [ ] One logical change per PR; eval harness run after each.
- [ ] `CHANGELOG.md` updated with the correct semver bump and human-readable notes.
- [ ] Cross-platform skills ship from one canonical core via wrappers, never forked bodies.
- [ ] Pinned version recorded for consumers (`skills-lock.json` or marketplace tag).

---

*Every mechanism above cites a finding from the corpus. Git mechanics (PRs, CI YAML, branch hygiene) are general engineering practice and are presented as the carrier for the finding-cited skill-lifecycle rules, not as authoring claims in their own right.*
