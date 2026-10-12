#!/usr/bin/env python3
"""Blind-administration prep for the SKILL.md §2.1 description-optimization loop.

Builds, under --out-dir (an eval workspace OUTSIDE every skill package —
target-skill-clean rule):
  - roster.md          : every skill's frontmatter description (the trigger surface)
  - answer-key.tsv     : qid <TAB> skill <TAB> srcnum <TAB> expected <TAB> query
  - blind-batch-NN.md  : shuffled query batches (qid + query only) for Executor
                         subagents — opaque, order-stable ids assigned AFTER the
                         seeded shuffle so the id carries no source-skill or
                         ordering signal [generator-assessor-separation]

Queries are drawn from each skill's packaged evals/trigger-eval.md (§2.1 exportable
set). Deterministic given --seed. Read-only over --skills-dir.

Usage:
  prep_eval_loop.py --skills-dir <dir-of-skill-packages> --out-dir <eval-workspace>
                    [--batch-count N] [--seed N] [--skills name1,name2,...]

--skills scopes the run to a subset (plus nothing else): use it for seam-scoped
re-runs after a roster change — collisions are born at boundary edits, so re-test
the edited skills and their adjacent siblings, not the whole roster.
"""
import argparse
import random
import re
import sys
from pathlib import Path


def frontmatter_description(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return ""
    lines = m.group(1).split("\n")
    desc_lines = []
    in_desc = False
    for line in lines:
        if re.match(r"^description:\s*>?-?\s*$", line):
            in_desc = True
            continue
        m2 = re.match(r"^description:\s*(\S.*)$", line)
        if m2:
            desc_lines.append(m2.group(1))
            in_desc = True
            continue
        if in_desc:
            if re.match(r"^\S", line):  # next top-level key
                break
            desc_lines.append(line.strip())
    return " ".join(l for l in desc_lines if l).strip()


def parse_eval_set(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(trigger|abstain)\s*\|", line)
        if m:
            q = m.group(2).strip().strip('"').strip("“”").strip()
            rows.append((int(m.group(1)), q, m.group(3)))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skills-dir", required=True, type=Path,
                    help="directory whose child dirs are skill packages (each with SKILL.md)")
    ap.add_argument("--out-dir", required=True, type=Path,
                    help="eval workspace to write roster/key/batches into (created if missing)")
    ap.add_argument("--batch-count", type=int, default=8,
                    help="number of blind batches (default 8)")
    ap.add_argument("--seed", type=int, default=7,
                    help="shuffle seed — fix it to make a run reproducible (default 7)")
    ap.add_argument("--skills", default="",
                    help="comma-separated skill names to scope to (seam-scoped re-runs); default all")
    args = ap.parse_args()

    subset = {s.strip() for s in args.skills.split(",") if s.strip()}
    skills = sorted(
        d for d in args.skills_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
        and (not subset or d.name in subset)
    )
    if subset:
        unknown = subset - {d.name for d in skills}
        if unknown:
            print(f"ERROR: --skills names not found under {args.skills_dir}: "
                  f"{', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
    if not skills:
        print(f"ERROR: no skill packages (dirs with SKILL.md) under {args.skills_dir}",
              file=sys.stderr)
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)

    roster_lines = ["# Skill roster — frontmatter descriptions (trigger surface)\n"]
    key_rows = []
    problems = []

    for d in skills:
        name = d.name
        desc = frontmatter_description(d / "SKILL.md")
        if not desc:
            problems.append(f"NO DESCRIPTION: {name}")
        roster_lines.append(f"## {name}\n\n{desc}\n")
        ev = d / "evals" / "trigger-eval.md"
        if not ev.exists():
            problems.append(f"NO EVAL SET: {name}")
            continue
        rows = parse_eval_set(ev)
        if len(rows) < 15:
            problems.append(f"PARSE SUSPECT ({len(rows)} rows): {name}")
        for num, query, expected in rows:
            key_rows.append((name, num, expected, query))

    # Opaque ids assigned AFTER the seeded shuffle (no source/order signal).
    rng = random.Random(args.seed)
    rng.shuffle(key_rows)
    key_rows = [
        (f"Q{i+1:03d}", name, num, expected, query)
        for i, (name, num, expected, query) in enumerate(key_rows)
    ]

    (args.out_dir / "roster.md").write_text("\n".join(roster_lines), encoding="utf-8")

    with (args.out_dir / "answer-key.tsv").open("w", encoding="utf-8") as f:
        f.write("qid\tskill\tsrcnum\texpected\tquery\n")
        for qid, name, num, expected, query in key_rows:
            f.write(f"{qid}\t{name}\t{num}\t{expected}\t{query}\n")

    per = (len(key_rows) + args.batch_count - 1) // args.batch_count
    for b in range(args.batch_count):
        chunk = key_rows[b * per:(b + 1) * per]
        lines = [f"# Blind batch {b+1:02d} — {len(chunk)} queries\n"]
        for qid, _name, _num, _expected, query in chunk:
            lines.append(f"- `{qid}` — {query}")
        (args.out_dir / f"blind-batch-{b+1:02d}.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8")

    print(f"skills: {len(skills)}")
    print(f"queries: {len(key_rows)}")
    print(f"batches: {args.batch_count} x ~{per}")
    for p in problems:
        print("WARN:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
