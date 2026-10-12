#!/usr/bin/env python3
"""Ledger grep-audit: scan a user's authored artifacts for any *do-not-reintroduce* phrase
recorded in their profile's `Confirmed Facts & Retractions` ledger.

The do-not-reintroduce list is **sourced from the profile ledger** (data-driven) — never
hard-coded — so the ledger stays the single source of truth. The audit is **read-only**: it
reports reintroductions and exits non-zero; it makes no edits.

Source of truth: kb/self/profile.md → "## Confirmed Facts & Retractions". Each retraction
entry may carry a clause like:  *Do-not-reintroduce:* "$1.12M IRR", or "right-sizing" as ...
From that clause this tool extracts:
  - quoted phrases verbatim (e.g. "$1.12M IRR", "right-sizing");
  - ALL-CAPS acronyms (e.g. DMAT) not already inside a quoted phrase;
  - money / multiplier figures (e.g. $500K, 100x) not already inside a quoted phrase.

Severity:
  FAIL  — specific figures / acronyms (contain a digit, "$", or are an ALL-CAPS acronym).
          A literal reappearance is almost certainly a reintroduction.
  WARN  — contextual common words (e.g. "right-sizing"): flagged for human verification because
          the ledger forbids them only in a specific sense, which grep can't disambiguate.

Exit code: 0 = no reintroductions found (WARNs allowed); 1 = at least one match (FAIL or WARN).

Usage:
  python audit_ledger.py                       # auto-detects the user when users/ has exactly one
  python audit_ledger.py --user <user-id>
  python audit_ledger.py --profile PATH --scan GLOB [--scan GLOB ...] [--include-archive]

Default scan set: artifacts/company-targets/**, artifacts/marketing/**,
artifacts/interview/**, career-journal.md.
artifacts/negotiation/** is deliberately excluded (see the comment at the scans list).
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

LEDGER_HEADING = "Confirmed Facts & Retractions"
DNR_MARKER = re.compile(r"do-?not-?reintroduce", re.IGNORECASE)
QUOTE_RE = re.compile(r'["\u201c\u201d]([^"\u201c\u201d]+)["\u201c\u201d]')
ALLCAPS_RE = re.compile(r"\b[A-Z]{3,}\b")
MONEY_RE = re.compile(r"\$\d[\d.,]*\s*[KMB]?\b", re.IGNORECASE)
MULTIPLIER_RE = re.compile(r"\b\d+(?:\.\d+)?x\b", re.IGNORECASE)
# Repo root = three levels up from this script (.claude/skills/ops-session-handoff/scripts/).
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def repo(*parts: str) -> str:
    return os.path.join(REPO_ROOT, *parts)


def strip_md(text: str) -> str:
    """Drop bold/italic markers so token extraction sees clean words."""
    return re.sub(r"[*_`]", "", text)


def find_section(text: str, heading: str) -> str:
    """Return the body of a `## heading` section up to the next `## ` heading (or EOF)."""
    m = re.search(r"(?im)^#{1,6}\s+" + re.escape(heading) + r"\s*$", text)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"(?im)^#{1,6}\s+\S", text[start:])
    return text[start: start + nxt.start()] if nxt else text[start:]


def split_entries(section: str) -> list[str]:
    """Split a ledger section into bullet entries (each starts with '- '), joining wrapped lines."""
    entries: list[str] = []
    cur: list[str] = []
    for line in section.splitlines():
        if re.match(r"^\s*-\s+", line):
            if cur:
                entries.append(" ".join(cur).strip())
            cur = [line.strip().lstrip("-").strip()]
        elif cur and line.strip():
            cur.append(line.strip())
        elif cur and not line.strip():
            entries.append(" ".join(cur).strip())
            cur = []
    if cur:
        entries.append(" ".join(cur).strip())
    return entries


def entry_label(entry: str) -> str:
    """Human label for an entry = its first bolded segment (date + verdict + subject)."""
    m = re.search(r"\*\*(.+?)\*\*", entry)
    return strip_md(m.group(1)).strip(" .") if m else strip_md(entry[:60]).strip()


def extract_phrases(profile_text: str) -> list[dict]:
    """Build the do-not-reintroduce phrase list from the profile ledger (data-driven)."""
    section = find_section(profile_text, LEDGER_HEADING)
    if not section:
        return []
    phrases: list[dict] = []
    seen: set[str] = set()

    for entry in split_entries(section):
        m = DNR_MARKER.search(entry)
        if not m:
            continue
        label = entry_label(entry)
        clause = strip_md(entry[m.end():])
        clause = clause.lstrip(":* ").strip()

        quoted = [q.strip() for q in QUOTE_RE.findall(strip_md(entry[m.end():])) if q.strip()]
        tokens: list[tuple[str, str]] = [(q, "hard") for q in quoted]

        # ALL-CAPS acronyms + money/multiplier figures not already inside a quoted phrase.
        quoted_lc = " ".join(quoted).lower()
        for tok in ALLCAPS_RE.findall(clause):
            if tok.lower() not in quoted_lc:
                tokens.append((tok, "hard"))
        for tok in MONEY_RE.findall(clause) + MULTIPLIER_RE.findall(clause):
            t = tok.strip()
            if t.lower() not in quoted_lc:
                tokens.append((t, "hard"))

        for phrase, _ in tokens:
            sev = classify(phrase)
            key = phrase.lower()
            if key in seen:
                continue
            seen.add(key)
            phrases.append({"phrase": phrase, "severity": sev, "label": label})
    return phrases


def classify(phrase: str) -> str:
    """FAIL for specific figures/acronyms; WARN for contextual common words."""
    if re.search(r"[\d$]", phrase):
        return "FAIL"
    if re.fullmatch(r"[A-Z]{3,}", phrase):
        return "FAIL"
    return "WARN"


def compile_matcher(phrase: str) -> re.Pattern:
    """Case-insensitive matcher with loose boundaries (figures contain $, digits, hyphens)."""
    return re.compile(r"(?<![\w$])" + re.escape(phrase) + r"(?![\w])", re.IGNORECASE)


STRIKE_RE = re.compile(r"~~(.+?)~~")
RETRACTED_MARKER = re.compile(r"retracted|do-?not-?reintroduce", re.IGNORECASE)


def is_compliant(line: str, span: tuple[int, int]) -> bool:
    """A match is compliant (not a reintroduction) if the phrase is struck through (~~...~~)
    or the line explicitly marks it RETRACTED / do-not-reintroduce — i.e. it's documenting the
    retraction, not reusing the claim.

    This is the sanctioned way to *cite* a retracted phrase (L-9): the marker must
    share the line with the quote — a heading or preceding paragraph saying
    "retracted" does not exempt lines below it. Correction notes should quote the
    phrase struck through (~~phrase~~) or say "retracted" in the same sentence,
    never rephrase to dodge the guard. Suppressed citations are counted and
    reported so the escape stays visible, never silent."""
    s, e = span
    for m in STRIKE_RE.finditer(line):
        if m.start() <= s and e <= m.end():
            return True
    return bool(RETRACTED_MARKER.search(line))


def gather_files(scans: list[str], include_archive: bool, exclude: set[str]) -> list[str]:
    files: list[str] = []
    for pattern in scans:
        for path in glob.glob(pattern, recursive=True):
            ap = os.path.abspath(path)
            if not os.path.isfile(ap) or not ap.endswith(".md"):
                continue
            if ap in exclude:
                continue
            if not include_archive and ("/_archive/" in ap or "/archive/" in ap):
                continue
            files.append(ap)
    return sorted(set(files))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", help="path to the profile ledger (default: kb/self/profile.md)")
    ap.add_argument("--scan", action="append", default=[], help="glob(s) of artifacts to scan (repeatable)")
    ap.add_argument("--include-archive", action="store_true", help="also scan archive/ folders")
    args = ap.parse_args()

    profile_path = args.profile or repo("kb", "self", "profile.md")
    if not os.path.isfile(profile_path):
        print(f"ERROR: profile not found: {profile_path}", file=sys.stderr)
        return 2

    scans = args.scan or [
        repo("kb", "world", "targets", "**", "*.md"),
        repo("kb", "artifacts", "applications", "**", "*.md"),
        repo("kb", "artifacts", "marketing", "**", "*.md"),
        repo("kb", "artifacts", "interview", "**", "*.md"),
        repo("kb", "self", "career-journal.md"),
        # kb/artifacts/negotiation/ is DELIBERATELY excluded (M5 decision, 2026-07-04):
        # internal-only artifacts where legitimate comp figures (e.g. the ~$500K comp-path
        # target) collide with ledger tokens (the retracted DMAT "$500K"). Scan it manually
        # via --scan only with that false positive in mind.
    ]

    with open(profile_path, encoding="utf-8") as fh:
        profile_text = fh.read()

    phrases = extract_phrases(profile_text)
    if not phrases:
        print(f"No do-not-reintroduce phrases found in {os.path.relpath(profile_path, REPO_ROOT)} "
              f"(ledger section '{LEDGER_HEADING}'). Nothing to audit.")
        return 0

    print("Ledger grep-audit — do-not-reintroduce phrases (sourced from the profile ledger):")
    for p in phrases:
        print(f"  [{p['severity']:>4}] {p['phrase']!r}  ← {p['label']}")
    print()

    files = gather_files(scans, args.include_archive, exclude={os.path.abspath(profile_path)})
    print(f"Scanning {len(files)} file(s) under:")
    for s in scans:
        print(f"  {os.path.relpath(s, REPO_ROOT)}")
    print()

    matchers = [(p, compile_matcher(p["phrase"])) for p in phrases]
    findings: list[tuple[str, str]] = []  # (severity, message)
    suppressed = 0  # compliant citations (struck-through / same-line retraction marker)

    for path in files:
        rel = os.path.relpath(path, REPO_ROOT)
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
        for lineno, line in enumerate(lines, 1):
            for p, rx in matchers:
                m = rx.search(line)
                if not m:
                    continue
                if is_compliant(line, m.span()):
                    suppressed += 1
                    continue
                sev = p["severity"]
                note = "" if sev == "FAIL" else "  (contextual — verify the forbidden sense)"
                msg = (f"{sev}  {rel}:{lineno}  matched {p['phrase']!r}{note}\n"
                       f"        ledger: {p['label']}\n"
                       f"        > {line.strip()[:160]}")
                findings.append((sev, msg))

    cite_note = (f" ({suppressed} compliant citation(s) suppressed — struck-through "
                 f"or same-line retraction marker)" if suppressed else "")
    if not findings:
        print(f"PASS — no do-not-reintroduce phrases found in scanned artifacts.{cite_note}")
        return 0

    fails = [m for s, m in findings if s == "FAIL"]
    warns = [m for s, m in findings if s == "WARN"]
    for m in fails + warns:
        print(m)
    print()
    print(f"Found {len(fails)} FAIL and {len(warns)} WARN reintroduction(s).{cite_note} "
          f"Read-only scan — no edits made.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
