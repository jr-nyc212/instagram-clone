#!/usr/bin/env bash
#
# validate.sh — Level 1 deterministic structural validator for SKILL.md packages
# ==============================================================================
# Implements the BMAD-style 19-rule / 6-category deterministic validation model
# described in references/audit-rubric.md §9. Zero inference cost; consistent
# across runs. Runs BEFORE any LLM-based (Level 2) review — never instead of it.
# [bmad-deterministic-skill-validator]
#
# Critical limitation: deterministic rules cannot catch semantic errors. A file
# passing all rules here may still behave incorrectly. Level 1 PASS is necessary
# but not sufficient. [bmad-deterministic-skill-validator]
#
# Portable: pure POSIX-ish bash + grep/sed/awk. No platform-specific tooling, no
# network. Works in CI on Claude Code, Cursor, Copilot, Codex, or locally.
#
# Usage:   bash scripts/validate.sh ./path-to-skill-directory
# Exit:    0 = PASS (no errors; warnings allowed)   1 = FAIL (>=1 error)
#          2 = usage error
# ==============================================================================

set -u

RESERVED_WORDS_REGEX='anthropic|claude'
NAME_REGEX='^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
DESC_MAX=1024

errors=0
warns=0
err()  { printf '  [FAIL] %s\n' "$1"; errors=$((errors+1)); }
warn() { printf '  [WARN] %s\n' "$1"; warns=$((warns+1)); }
ok()   { printf '  [ ok ] %s\n' "$1"; }

# ---- argument handling -------------------------------------------------------
if [ $# -ne 1 ]; then
  echo "usage: bash scripts/validate.sh ./skill-directory" >&2
  exit 2
fi
DIR="${1%/}"
if [ ! -d "$DIR" ]; then
  echo "error: '$DIR' is not a directory" >&2
  exit 2
fi
# Resolve to an absolute path so 'validate.sh .' compares against the real
# directory name, not the literal '.'
ABS_DIR="$(cd "$DIR" 2>/dev/null && pwd)"
DIRNAME="$(basename "$ABS_DIR")"
SKILL="$DIR/SKILL.md"

echo "Level 1 deterministic validation: $DIR"
echo "------------------------------------------------------------"

# ============================================================================
# CATEGORY 1 — Naming conventions
# ============================================================================
echo "Category 1: Naming conventions"

# Rule 1.1 — SKILL.md exists and is named with all-uppercase SKILL
if [ -f "$SKILL" ]; then
  ok "SKILL.md present (uppercase)"
else
  # detect a wrong-case variant for a clearer message
  alt="$(find "$DIR" -maxdepth 1 -iname 'skill.md' ! -name 'SKILL.md' 2>/dev/null | head -n1)"
  if [ -n "$alt" ]; then
    err "skill file must be named 'SKILL.md' (uppercase); found '$(basename "$alt")'"
  else
    err "no SKILL.md found in $DIR"
  fi
  echo "------------------------------------------------------------"
  echo "Cannot continue without SKILL.md. FAIL."
  exit 1
fi

# Extract frontmatter (between the first two '---' lines)
FM="$(awk 'NR==1 && $0!="---"{exit} NR==1{next} /^---[[:space:]]*$/{exit} {print}' "$SKILL")"
if [ -z "$FM" ]; then
  err "missing YAML frontmatter (file must begin with a '---' fenced block)"
fi

# Rule 1.2 — name field present
NAME="$(printf '%s\n' "$FM" | sed -n 's/^name:[[:space:]]*//p' | head -n1 | tr -d '"'\''' | sed 's/[[:space:]]*$//')"
if [ -z "$NAME" ]; then
  err "frontmatter missing 'name' field"
else
  # Rule 1.3 — name character class + length
  if printf '%s' "$NAME" | grep -Eq "$NAME_REGEX"; then ok "name '$NAME' matches [a-z0-9-] with no leading/trailing/edge hyphen"; else
    err "name '$NAME' invalid: lowercase [a-z0-9-] only, no leading/trailing/consecutive hyphens"
  fi
  if printf '%s' "$NAME" | grep -q -- '--'; then err "name '$NAME' contains consecutive hyphens"; fi
  nlen=${#NAME}
  if [ "$nlen" -ge 1 ] && [ "$nlen" -le 64 ]; then ok "name length $nlen (1-64)"; else err "name length $nlen out of range (1-64)"; fi
  # Rule 1.4 — name matches parent directory
  if [ "$NAME" = "$DIRNAME" ]; then ok "name matches directory '$DIRNAME'"; else
    err "name '$NAME' does not match parent directory '$DIRNAME'"
  fi
fi

# ============================================================================
# CATEGORY 2 — Variable usage (reserved words, description sanity)
# ============================================================================
echo "Category 2: Variable usage / reserved words"

# Rule 2.1 — reserved words forbidden in name
if [ -n "$NAME" ] && printf '%s' "$NAME" | grep -Eiq "$RESERVED_WORDS_REGEX"; then
  err "name contains a reserved word (anthropic/claude)"
else
  ok "name free of reserved words"
fi

# Rule 2.2 — description present and within cap
DESC="$(printf '%s\n' "$FM" | awk '/^description:/{f=1} f{print} /^[a-z_-]+:/ && !/^description:/ && NR>1{if(f && !/^description:/) exit}' | sed '1s/^description:[[:space:]]*//')"
# simpler: grab description line + following indented/folded lines
DESC="$(awk '
  /^description:/{cap=1; line=$0; sub(/^description:[[:space:]]*>?[[:space:]]*/,"",line); buf=line; next}
  cap && /^[[:space:]]+/{l=$0; sub(/^[[:space:]]+/,"",l); buf=buf" "l; next}
  cap && /^[A-Za-z_-]+:/{cap=0}
  END{print buf}
' <<EOF
$FM
EOF
)"
DESC="$(printf '%s' "$DESC" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
if [ -z "$DESC" ]; then
  err "frontmatter missing 'description' field"
else
  dlen=${#DESC}
  if [ "$dlen" -le "$DESC_MAX" ]; then ok "description length $dlen (<= $DESC_MAX)"; else
    err "description length $dlen exceeds open-standard cap of $DESC_MAX chars"
  fi
  if [ "$dlen" -lt 40 ]; then warn "description is very short ($dlen chars) — likely lacks What/When/Capabilities and trigger phrases"; fi
  # Rule 2.3 — no XML angle brackets in description
  if printf '%s' "$DESC" | grep -q '<[^>]*>'; then err "description contains XML/angle-bracket tags (not allowed)"; else ok "description has no XML tags"; fi
fi

# ============================================================================
# CATEGORY 3 — Path references (no absolute paths / internal leakage)
# ============================================================================
echo "Category 3: Path references"

# Rule 3.1 — no absolute filesystem paths in the body (encapsulation PATH-05)
ABS_HITS="$(grep -nE '(^|[^a-zA-Z0-9_])/(home|Users|root|var|tmp|etc|opt)/' "$SKILL" | grep -v '${CLAUDE_SKILL_DIR}' || true)"
if [ -n "$ABS_HITS" ]; then
  err "absolute path(s) found (use relative paths or \${CLAUDE_SKILL_DIR}):"
  printf '%s\n' "$ABS_HITS" | sed 's/^/         /'
else
  ok "no leaked absolute paths"
fi

# Rule 3.2 — referenced reference/adapter/template files actually exist
MISSING=0
while IFS= read -r ref; do
  [ -z "$ref" ] && continue
  if [ ! -e "$DIR/$ref" ]; then warn "SKILL.md references '$ref' which is not present in the package"; MISSING=$((MISSING+1)); fi
done <<EOF
$(grep -oE '(references|adapters|templates|scripts|examples|evals)/[A-Za-z0-9._/-]+' "$SKILL" | sort -u)
EOF
[ "$MISSING" -eq 0 ] && ok "all referenced package paths resolve"

# ============================================================================
# CATEGORY 4 — Invocation syntax (frontmatter fences, tool grants)
# ============================================================================
echo "Category 4: Invocation syntax"

# Rule 4.1 — frontmatter is properly fenced (opens and closes with ---)
fence_count="$(grep -cE '^---[[:space:]]*$' "$SKILL")"
if [ "$fence_count" -ge 2 ]; then ok "frontmatter fences present (>=2 '---')"; else
  err "frontmatter not properly fenced (need opening and closing '---')"
fi

# Rule 4.2 — allowed-tools grant inflation warning
if printf '%s' "$FM" | grep -Eq '^allowed-tools:.*Bash\(\*\)'; then
  warn "allowed-tools grants Bash(*) — broad authority; scope to specific commands"
fi

# ============================================================================
# CATEGORY 5 — Sequence correctness (body size, required intent content)
# ============================================================================
echo "Category 5: Sequence correctness / size"

# Rule 5.1 — body under 500 lines
TOTAL_LINES="$(wc -l < "$SKILL" | tr -d ' ')"
if [ "$TOTAL_LINES" -le 500 ]; then ok "SKILL.md is $TOTAL_LINES lines (<= 500)"; else
  err "SKILL.md is $TOTAL_LINES lines (exceeds 500-line guidance; split into references/)"
fi

# Rule 5.2 — Stop Rules present (most commonly omitted intent component)
if grep -qiE 'stop rule' "$SKILL"; then ok "Stop Rules section present"; else
  warn "no 'Stop Rules' found — the most commonly omitted intent component; confirm it is intentional"
fi

# Rule 5.3 — at least one finding citation present (this package's convention)
if grep -qE '\[[a-z0-9][a-z0-9-]+\]' "$SKILL"; then ok "finding citations present"; else
  warn "no [finding-name] citations found — package convention requires sourced claims"
fi

# ============================================================================
# CATEGORY 6 — Encapsulation boundaries (template/comment leakage, anti-patterns)
# ============================================================================
echo "Category 6: Encapsulation boundaries"

# Rule 6.1 — no leftover template elicitation comments in a shipped skill
if grep -q 'TACIT KNOWLEDGE PROMPT' "$SKILL"; then
  warn "leftover 'TACIT KNOWLEDGE PROMPT' template comments — delete before publishing"
else
  ok "no leftover template comments"
fi

# Rule 6.2 — reasoning-model anti-pattern heuristics (degrade frontier models).
# Exclude lines that merely *discuss* the anti-pattern (citations, the words
# "anti-pattern"/"degrade"/"do not"/"avoid"/"remove") to cut false positives on
# meta-content that documents the rule.
AP_HITS="$(grep -inE 'think step by step|chain[ -]of[ -]thought|few[ -]shot' "$SKILL" \
  | grep -ivE 'anti-pattern|degrade|do not|don.t|avoid|remove|never|reasoning-model|prescribed' || true)"
if [ -n "$AP_HITS" ]; then
  warn "possible prescribed-reasoning anti-pattern (CoT/few-shot) in instruction text — audit before porting [reasoning-model-anti-pattern-prescribed-reasoning]:"
  printf '%s\n' "$AP_HITS" | sed 's/^/         /'
else
  ok "no obvious prescribed-reasoning anti-patterns in instruction text"
fi

# ============================================================================
# CATEGORY 7 — Capability contract (universal bar, MV45; §4.0 sidecar)
# ============================================================================
echo "Category 7: Capability contract (universal bar)"

CONTRACT="$DIR/capability-contract.yaml"
if [ ! -f "$CONTRACT" ]; then
  warn "no capability-contract.yaml at skill root — universal audit machinery (MV45 §1.3); required once this skill's MV45 S2 retrofit lands"
else
    ok "capability-contract.yaml present"
    if grep -qE '^schema-version:[[:space:]]*1[[:space:]]*$' "$CONTRACT"; then ok "schema-version 1"; else
      err "capability-contract.yaml missing 'schema-version: 1'"
    fi
    # every '- id:' block must carry tier/purpose/degradation before the next block
    PARSE_ERRS="$(awk '
      function flush() {
        if (id != "") {
          if (tier == "") print "capability " id " missing tier"
          else if (tier != "required" && tier != "optional") print "capability " id " tier is " tier " (need required|optional)"
          if (!hasp) print "capability " id " missing purpose"
          if (!hasd) print "capability " id " missing degradation"
          n++
        }
      }
      /^[[:space:]]*-[[:space:]]*id:/ { flush(); id=$0; sub(/^[[:space:]]*-[[:space:]]*id:[[:space:]]*/,"",id); gsub(/["[:space:]]/,"",id); tier=""; hasp=0; hasd=0; next }
      /^[[:space:]]*tier:/    { tier=$0; sub(/^[[:space:]]*tier:[[:space:]]*/,"",tier); gsub(/["[:space:]]/,"",tier) }
      /^[[:space:]]*purpose:[[:space:]]*[^[:space:]]/     { hasp=1 }
      /^[[:space:]]*degradation:[[:space:]]*[^[:space:]]/ { hasd=1 }
      END { flush(); if (n == 0) print "no capabilities declared (need at least one - id: block)" }
    ' "$CONTRACT")"
    if [ -n "$PARSE_ERRS" ]; then
      while IFS= read -r perr; do [ -n "$perr" ] && err "capability-contract.yaml: $perr"; done <<EOF
$PARSE_ERRS
EOF
    else
      ok "every capability carries id / tier / purpose / degradation"
    fi
    # vocabulary membership (WARN) — vocabulary ships with this script's package
    VOCAB="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)/references/capability-vocabulary.md"
    if [ -f "$VOCAB" ]; then
      while IFS= read -r cid; do
        [ -z "$cid" ] && continue
        if ! grep -q "\`$cid\`" "$VOCAB"; then
          warn "capability id '$cid' not in the controlled vocabulary (references/capability-vocabulary.md)"
        fi
      done <<EOF
$(grep -E '^[[:space:]]*-[[:space:]]*id:' "$CONTRACT" | sed 's/^[[:space:]]*-[[:space:]]*id:[[:space:]]*//' | tr -d '\" ')
EOF
      ok "vocabulary membership checked"
    else
      warn "controlled vocabulary not found next to this script — vocabulary check skipped"
    fi
fi

# ============================================================================
# Summary
# ============================================================================
echo "------------------------------------------------------------"
printf 'Result: %d error(s), %d warning(s)\n' "$errors" "$warns"
if [ "$errors" -gt 0 ]; then
  echo "Level 1: FAIL — fix structural errors before Level 2 (four-discipline rubric)."
  exit 1
fi
echo "Level 1: PASS — necessary but not sufficient. Proceed to Level 2 with a SEPARATE Grader context."
exit 0
