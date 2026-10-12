# Template — Description Optimization Eval Set

> 20-query template for the description optimization loop (§2.1). Triggering
> accuracy is empirically measurable, not heuristic
> `[skill-description-optimization-loop-held-out-test]`.

## How to use

1. Replace every `<...>` placeholder with realistic queries **for the skill you
   are tuning**. Realistic and specific wins: a query with file paths, real
   company names, or casual speech is GOOD; "Format this data" is BAD.
   **Exportable skills (§2.1): specific-but-fictional only** — the set ships in
   the package as `evals/trigger-eval.md`, so phrasings must be user-content-free
   from the first draft. Seed intent shapes from a live capture corpus if the
   workspace keeps one (real phrasings reveal patterns like bare artifact-name
   invocations), but never copy a real phrasing verbatim; invent names, paths,
   and projects instead.
2. Build **8–10 should-trigger** (near-miss paraphrases of real requests) and
   **8–10 should-not-trigger** (near-miss keyword matches that actually need
   something else). 20 total.
3. Split **60/40 train/test**. Run each *train* query **3 times** (triggering is
   non-deterministic; 3 runs gives a reliable rate).
4. Iterate the description **≤ 5 times**.
5. Select the winning description by **TEST** score, not train score — this is
   the overfitting guard.
6. Remember: a model only triggers skills it cannot handle alone; trivial
   single-step queries may not trigger even with a perfect description.
7. **Exportable skills — graduate the finished set**: when the loop settles,
   distill winner queries into the package at `evals/trigger-eval.md`, each with
   its expected verdict (trigger / abstain / route-to-sibling). Receiving agents
   self-administer that file as the install acceptance check (no runner needed);
   this workspace copy remains iteration residue.

CLI (if your harness ships the loop runner):
`python -m scripts.run_loop --eval-set ./eval-query-set.md --skill-path ./<skill-dir> --model <id> --max-iterations 5`

---

## SHOULD-TRIGGER (target: high trigger rate)

### Train (6)
1. `<obvious in-domain request, casual phrasing>`
2. `<paraphrase using a synonym for the core action>`
3. `<request that names a real file path / artifact this skill consumes>`
4. `<request embedded in a larger multi-step ask where this skill is the right tool>`
5. `<request using the user's natural vocabulary, not the skill's jargon>`
6. `<edge-case in-domain request that is the most likely real failure mode>`

### Test (3 — held out, do not tune against)
7. `<in-domain request with different surface wording than any train query>`
8. `<in-domain request that mentions the deliverable, not the action>`
9. `<terse in-domain request (few words, still unambiguous)>`

---

## SHOULD-NOT-TRIGGER (target: low trigger rate / correct abstention)

### Train (6)
10. `<request that shares keywords but needs a different skill>`
11. `<adjacent-domain request this skill must NOT claim>`
12. `<request the base model handles fine alone (no skill needed)>`
13. `<request that names a similar artifact but a different operation>`
14. `<vague request that should ask for clarification, not trigger>`
15. `<request for the inverse / opposite operation>`

### Test (5 — held out)
16. `<near-miss keyword overlap, different intent>`
17. `<request belonging to a sibling skill in the same package>`
18. `<request that is in-domain topically but out-of-scope by constraint>`
19. `<trivial single-step request that should not trigger>`
20. `<ambiguous request resolvable only by asking the user>`

---

## Scoring sheet

| Iteration | Description (one-line diff) | Train trigger rate | Test trigger rate | Test false-trigger rate | Keep? |
|-----------|-----------------------------|--------------------|-------------------|-------------------------|-------|
| 0 (baseline) | | | | | |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Winner:** iteration with the best TEST trigger rate AND lowest TEST
false-trigger rate. Record it in `CHANGELOG.md` if it changes a shipped skill,
and re-run after any substantive body change (description drift)
`[description-based-workflow-routing-lazy-dispatch]`.
