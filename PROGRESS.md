# PROGRESS — Instagram clone

Updated: 2026-10-12 — Session 1: project scaffolding, skills, and working rules set up.
No HTML, CSS, or JS written. No git repo yet.

## Start here

Read `CLAUDE.md` for the working rules, then jump to **Current milestone** below.
Shipped work is in `HISTORY.md`. Reference material: `docs/lesson-plan.md` (steps with
collapsed answers) and `docs/assessment.md` (time and skills estimate). Type
`/github-flow` for the git and gh commands.

## North Star

A finished Instagram-style feed that matches the Scrimba design, built with semantic
HTML and flexbox, published on GitHub through the issue → branch → PR → merge flow.
Stretch: the feed is rendered from the `posts` array with JavaScript, and likes
increment on click.

## Roadmap

- [>] M1 — Core: first post hand-written in semantic HTML, styled to match the design,
  icons fade on hover, merged to main on GitHub.
- [ ] M2 — Stretch 1: all three posts rendered from the `posts` array with a loop.
- [ ] M3 — Stretch 2: clicking the heart increments that post's like count.
- [ ] M4 — Polish: portfolio README via `/scrimba-readme`, Netlify deploy.

## Current milestone — M1 Core

**Definition of done:** `index.html` has a top bar and one post with header, image,
icon row, likes, and caption, all semantic elements. CSS centers a fixed-width column
and matches the design. Icons go translucent on hover. Merged to main on GitHub.

**Scopes (hill status)**

- setup — git init, GitHub repo, issue #1, branch `first-post`, head metadata — uphill.
  Nothing run yet. `/github-flow` step 0 then step 1.
- html-first-post — semantic markup for the top bar and one post — uphill
- css-layout — column, header row, full-width image, icon row, text styles — uphill
- hover — opacity on icon hover and focus — uphill
- publish — commit, push, PR "Closes #1", merge — uphill

**Next unit of work:** `setup`. Run `npm install`, then the step 0 commands from
`/github-flow`. Screenshot the Scrimba design into `docs/design/` before css-layout.

## Backlog / Icebox

- Double-click on the post image to like (Instagram behaviour).
- Replace the boilerplate README (`/scrimba-readme`).
- Deploy to Netlify like NFT-Site and WCAG_project.

## Blockers / risks

- No design image in the starter folder. Screenshot the scrim into `docs/design/`
  before starting the CSS.

## Decisions & findings

- Working style: the student asks, Claude answers with a short why and the code, no
  quizzes. Canonical home: `CLAUDE.md`.
- This project is self-contained. Its `CLAUDE.md`, `docs/`, and `.claude/skills` are
  the only sources of rules; nothing outside the folder is referenced.
