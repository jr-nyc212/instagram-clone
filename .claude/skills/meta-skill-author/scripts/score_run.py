#!/usr/bin/env python3
"""Score Executor verdicts against the answer key (Comparator role, §3.1).

Pass/fail rule per trigger-eval.md semantics: a query tests whether its SOURCE
skill activates. expected=trigger -> pass iff verdict == source skill.
expected=abstain -> pass iff verdict != source skill (routing elsewhere or none
both count as correct abstention for the source skill).

Verdicts-file format: one `qid -> verdict` line per query (backticks tolerated).
With multiple verdict files, a query fails only if it fails in a MAJORITY of the
runs it appears in (re-run protocol: persistent mismatches only).

Usage:
  score_run.py [--key answer-key.tsv] <verdicts-file> [more-verdicts-files...]

--key defaults to answer-key.tsv beside the first verdicts file (the layout
prep_eval_loop.py writes).
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--key", type=Path, default=None,
                    help="answer-key.tsv path (default: beside the first verdicts file)")
    ap.add_argument("verdicts", nargs="+", type=Path,
                    help="one or more verdicts files (qid -> verdict lines)")
    args = ap.parse_args()

    key_path = args.key or (args.verdicts[0].resolve().parent / "answer-key.tsv")
    if not key_path.exists():
        print(f"ERROR: answer key not found: {key_path}", file=sys.stderr)
        return 2

    key = {}
    with key_path.open(encoding="utf-8") as f:
        next(f)
        for line in f:
            qid, skill, srcnum, expected, query = line.rstrip("\n").split("\t")
            key[qid] = (skill, expected, query)

    runs = []
    for path in args.verdicts:
        verdicts = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if "->" in line:
                qid, v = [x.strip().strip("`") for x in line.split("->", 1)]
                verdicts[qid] = v
        runs.append(verdicts)

    def passes(qid, verdict):
        skill, expected, _ = key[qid]
        return (verdict == skill) if expected == "trigger" else (verdict != skill)

    per_skill = defaultdict(lambda: {"t_pass": 0, "t_all": 0, "a_pass": 0, "a_all": 0})
    failures = []
    missing = []

    for qid, (skill, expected, query) in sorted(key.items()):
        results = [(passes(qid, r[qid]), r[qid]) for r in runs if qid in r]
        if not results:
            missing.append(qid)
            continue
        n_pass = sum(1 for ok, _ in results if ok)
        ok = n_pass * 2 > len(results)  # majority
        bucket = "t" if expected == "trigger" else "a"
        per_skill[skill][f"{bucket}_all"] += 1
        if ok:
            per_skill[skill][f"{bucket}_pass"] += 1
        else:
            failures.append((qid, skill, expected, [v for _, v in results], query))

    tot_pass = sum(s["t_pass"] + s["a_pass"] for s in per_skill.values())
    tot_all = sum(s["t_all"] + s["a_all"] for s in per_skill.values())
    print(f"OVERALL: {tot_pass}/{tot_all} ({100*tot_pass/tot_all:.1f}%)   [runs: {len(runs)}]")
    if missing:
        print(f"MISSING VERDICTS: {len(missing)}: {', '.join(missing)}")
    print()
    print(f"{'skill':32} {'trigger':>10} {'abstain':>10} {'total':>8}")
    for skill in sorted(
        per_skill,
        key=lambda s: (per_skill[s]["t_pass"] + per_skill[s]["a_pass"])
        / max(1, per_skill[s]["t_all"] + per_skill[s]["a_all"]),
    ):
        s = per_skill[skill]
        tot = s["t_pass"] + s["a_pass"]
        alln = s["t_all"] + s["a_all"]
        flag = "  <-- " if tot < alln else ""
        print(f"{skill:32} {s['t_pass']:>4}/{s['t_all']:<4} {s['a_pass']:>4}/{s['a_all']:<4} {tot:>3}/{alln:<3}{flag}")

    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for qid, skill, expected, verdicts, query in failures:
            print(f"  {qid} [{skill} / {expected}] got {verdicts}\n       \"{query}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
