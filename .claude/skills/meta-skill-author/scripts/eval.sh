#!/usr/bin/env bash
#
# eval.sh — Level 1 gate + sibling eval-workspace scaffolder for SKILL.md packages
# ==============================================================================
# Makes a skill eval-ready and keeps the TARGET SKILL CLEAN: all eval scaffolds and
# run outputs live in a SIBLING "<skill-name>-workspace/" directory, never inside the
# skill. This matches Anthropic's official skill-creator, which puts results in a
# sibling workspace and treats the skill as the input.
#
# It does three things:
#   1. Runs validate.sh (Level 1 deterministic structural validation) on the target.
#   2. Prepares the sibling workspace and (with --init) scaffolds the eval artifacts
#      THERE, not in the target: a triggering eval set for every skill, plus — for
#      objectively-verifiable skills — a functional eval-cases stub.
#   3. Prints the Definition of Done and the ready-to-paste Grader subagent invocation
#      (agents/grader.md + references/audit-rubric.md), run in a SEPARATE context.
#      [generator-assessor-separation-in-skill-iteration]
#
# EXPORTABLE-SKILL EXCEPTION (SKILL.md §2.1/§6): iteration residue stays in the sibling
# workspace, but a skill that ships a capability-contract.yaml must ALSO carry the
# distilled set inside the package at evals/trigger-eval.md — query + expected verdict,
# generic by construction (specific-but-fictional phrasings; real user/workspace facts
# never travel). That file is the receiving side's install acceptance check; this gate
# verifies its presence for exportable targets.
#
# --subjective: for skills whose output is inherently subjective (writing voice/style,
#   tone, design, art). Functional binary assertions are NOT required for these — they
#   are evaluated qualitatively (a named scorecard + human review), per the rubric's
#   subjective-skill carve-out. Triggering optimization still applies to every skill.
#
# --deterministic: for skills whose core IS a tested program (renderer, parser, formatter,
#   validator — e.g. tool-resume-render). The functional guarantee comes from the script's
#   own tests, not an LLM assertion suite, so eval-cases.md is NOT required — verify by
#   running the bundled tests + Level 1, per the rubric's deterministic/script-core carve-out.
#   Triggering optimization still applies to every skill.
#
# Deterministic plumbing only; it does NOT grade content. Level 1 + eval presence is
# necessary but not sufficient. [bmad-deterministic-skill-validator]
#
# Usage:   bash scripts/eval.sh [--init] [--subjective|--deterministic] ./path-to-skill-directory
# Exit:    0 = ready (Level 1 PASS and required eval artifacts present)
#          1 = not ready (Level 1 FAIL or required eval artifacts missing/placeholder)
#          2 = usage error
# ==============================================================================

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PKG_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_EVAL_SET="$PKG_DIR/templates/eval-query-set.md"

INIT=0
SUBJECTIVE=0
DETERMINISTIC=0
DIR=""
for arg in "$@"; do
  case "$arg" in
    --init) INIT=1 ;;
    --subjective) SUBJECTIVE=1 ;;
    --deterministic) DETERMINISTIC=1 ;;
    -h|--help) echo "usage: bash scripts/eval.sh [--init] [--subjective|--deterministic] ./skill-directory"; exit 2 ;;
    *) DIR="${arg%/}" ;;
  esac
done

if [ "$SUBJECTIVE" -eq 1 ] && [ "$DETERMINISTIC" -eq 1 ]; then
  echo "error: pass at most one of --subjective / --deterministic" >&2
  exit 2
fi

if [ -z "$DIR" ]; then
  echo "usage: bash scripts/eval.sh [--init] [--subjective|--deterministic] ./skill-directory" >&2
  exit 2
fi
if [ ! -d "$DIR" ]; then
  echo "error: not a directory: $DIR" >&2
  exit 2
fi

SKILL_NAME="$(basename "$DIR")"
PARENT="$(cd "$(dirname "$DIR")" && pwd)"
WORKSPACE="$PARENT/${SKILL_NAME}-workspace"

ready=0
note() { printf '  %s\n' "$1"; }
fail() { printf '  [MISSING] %s\n' "$1"; ready=1; }
have() { printf '  [ ok ] %s\n' "$1"; }

echo "Eval readiness gate: $DIR"
echo "Sibling workspace:   $WORKSPACE"
echo "                     (eval artifacts + run outputs live here, NOT in the skill)"
[ "$SUBJECTIVE" -eq 1 ] && echo "Mode: subjective (qualitative eval; no bundled binary assertions required)"
[ "$DETERMINISTIC" -eq 1 ] && echo "Mode: deterministic/script-core (verify via bundled script tests; no LLM eval-cases required)"
echo "------------------------------------------------------------"

# ---- Step 1: Level 1 structural validation (on the target) ------------------
echo "Step 1: Level 1 structural validation (validate.sh)"
if bash "$SCRIPT_DIR/validate.sh" "$DIR" >/tmp/eval_validate.$$ 2>&1; then
  have "Level 1 PASS"
else
  ready=1
  printf '  [FAIL] Level 1 FAILED — see detail below:\n'
  sed 's/^/      /' /tmp/eval_validate.$$
fi
rm -f /tmp/eval_validate.$$
echo

# ---- Step 2: sibling workspace + eval artifacts (scaffold with --init) -------
echo "Step 2: Eval artifacts (in the sibling workspace)"
EVAL_SET="$WORKSPACE/trigger-eval-set.md"
EVAL_CASES="$WORKSPACE/eval-cases.md"

if [ "$INIT" -eq 1 ]; then
  mkdir -p "$WORKSPACE"
  if [ ! -f "$EVAL_SET" ] && [ -f "$TEMPLATE_EVAL_SET" ]; then
    cp "$TEMPLATE_EVAL_SET" "$EVAL_SET"
    note "scaffolded trigger-eval-set.md in workspace — fill in real queries"
  fi
  if [ "$SUBJECTIVE" -eq 0 ] && [ "$DETERMINISTIC" -eq 0 ] && [ ! -f "$EVAL_CASES" ]; then
    cat > "$EVAL_CASES" <<'STUB'
# Eval Cases (stub — fill before grading)

Functional capability assertions for an objectively-verifiable skill. Each assertion must
be binary so a separate Grader context can check it without judgment calls. Run outputs and
grading.json for each case also live in this workspace, organized by iteration.

## Capability cases
### C1 — <primary mode>
- **Input**: <realistic input>
- **Binary assertions**:
  - [ ] <assertion tied to an acceptance criterion>

## Regression anchors (lock once captured)
| Scenario | Gold artifact path | Status |
|----------|--------------------|--------|
| <mode>   | <path>             | PENDING |

## Acceptance-criteria -> assertion map
Map every SKILL.md acceptance criterion to a binary check above.
STUB
    note "scaffolded eval-cases.md stub in workspace — fill in real assertions"
  fi
fi

[ -f "$EVAL_SET" ] && have "trigger-eval-set.md present" || fail "trigger-eval-set.md (run with --init to scaffold)"

# ---- Exportable skills: distilled set must live IN the package -----------------
if [ -f "$DIR/capability-contract.yaml" ]; then
  PKG_EVAL="$DIR/evals/trigger-eval.md"
  if [ -f "$PKG_EVAL" ]; then
    have "evals/trigger-eval.md present (exportable: distilled set ships in the package)"
    if grep -q '<obvious in-domain request' "$PKG_EVAL" 2>/dev/null; then
      ready=1
      printf '  [TODO] evals/trigger-eval.md still contains template placeholders \xe2\x80\x94 distill the finished set\n'
    fi
  else
    fail "evals/trigger-eval.md (skill ships capability-contract.yaml \xe2\x86\x92 exportable \xe2\x86\x92 distilled eval set must ship in the package, \xc2\xa72.1)"
  fi
fi

if [ "$SUBJECTIVE" -eq 1 ]; then
  note "subjective skill: functional eval-cases NOT required — judge qualitatively with a named"
  note "scorecard (e.g. the skill's own review rubric) + a human-in-the-loop review loop."
elif [ "$DETERMINISTIC" -eq 1 ]; then
  note "deterministic/script-core skill: LLM eval-cases NOT required — verify via the skill's"
  note "own bundled script tests (or a documented golden-output check) + Level 1 above."
else
  [ -f "$EVAL_CASES" ] && have "eval-cases.md present" || fail "eval-cases.md (run with --init, or pass --subjective / --deterministic if output is not LLM-graded)"
fi

# placeholder detection: unfilled template slots still present
if [ -f "$EVAL_SET" ] && grep -q '<obvious in-domain request' "$EVAL_SET" 2>/dev/null; then
  ready=1
  printf '  [TODO] trigger-eval-set.md still contains template placeholders — fill real queries\n'
fi
echo

# ---- Step 3: Definition of Done + Grader handoff ----------------------------
echo "Step 3: Definition of Done (a skill is not 'done' until all are true)"
echo "  [ ] Level 1 validate.sh PASS"
echo "  [ ] trigger-eval-set.md filled: 20 queries, 60/40 train/test, winner by TEST score"
if [ -f "$DIR/capability-contract.yaml" ]; then
  echo "  [ ] evals/trigger-eval.md distilled: query + expected verdict, generic by construction"
fi
if [ "$SUBJECTIVE" -eq 1 ]; then
  echo "  [ ] qualitative review method documented (named scorecard + human review loop)"
elif [ "$DETERMINISTIC" -eq 1 ]; then
  echo "  [ ] bundled script tests (or golden-output check) pass alongside Level 1"
else
  echo "  [ ] eval-cases.md filled: binary capability assertions per mode"
fi
echo "  [ ] four-discipline rubric run by a SEPARATE Grader context (never self-grade)"
echo "  [ ] AUDIT RESULT recorded (PASS / handoff fixes applied) in the package CHANGELOG"
echo
echo "Run outputs (results, grading.json, benchmark) go under: $WORKSPACE"
echo "Next: spawn the Grader in a separate context using"
echo "  $PKG_DIR/agents/grader.md"
echo "substituting <SKILL_DIR>=$DIR — it reads references/audit-rubric.md (incl. the"
echo "subjective-skill carve-out) and emits the Enhancement Handoff Block. Do NOT grade"
echo "from the authoring context."
echo "------------------------------------------------------------"
if [ "$ready" -eq 0 ]; then
  echo "Result: READY for Level 2 grading."
else
  echo "Result: NOT READY — resolve the items above (try --init to scaffold), then re-run."
fi
exit "$ready"
