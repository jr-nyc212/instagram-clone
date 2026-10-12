---
name: github-flow
description: Reminder of the git and gh CLI commands for publishing a Scrimba lesson to GitHub (issue, branch, commit, push, PR, merge). Use when the user asks how to publish, start a lesson, create a repo, fix a git mistake, or types /github-flow.
---

# GitHub flow for Scrimba lessons

This is the flow from the portfolio-css repo, reconstructed from its history. The user
runs every command themselves in the VS Code terminal (Ctrl + backtick). Print the
commands for the step they are on, each with its one-line explanation. Do not run
them unless asked.

When invoked with no argument, first run `git status -sb` and `git branch --show-current`
(read-only) to work out which step the user is on, then show only that step.

## 0. First time only: turn a starter folder into a GitHub repo

```
git init -b main
```
Make this folder a repo whose first branch is `main`.

```
git add .
git commit -m "Project setup"
```
Stage everything and record the starting snapshot. "Project setup" is the message
used in portfolio-css.

```
gh repo create <repo-name> --public --source=. --remote=origin --push
```
Create the GitHub repo, connect this folder to it as `origin`, push `main`.

## 1. Start a lesson

```
git switch main
git pull --ff-only origin main
```
Be on `main` and make sure it matches GitHub before branching. `--ff-only` refuses to
create a merge commit, so if it fails something is off: stop and ask.

```
gh issue create --title "<what the lesson does>" --body "<one or two sentences>"
```
Create the issue. Note the number it prints; the PR body needs it.

```
git switch -c <short-slug>
```
Create the branch and move onto it. Slugs used before: `layout-basics`,
`roboto-font`, `h2-borders`, `accent-text`. Lowercase, hyphens, two or three words.

## 2. Do the work, then commit

```
git status
git diff
```
See what changed. Read the diff before committing; it's the last chance to catch a
stray edit.

```
git add .
git commit -m "<Imperative sentence describing the change>"
```
Messages from past repos: "Add Roboto light and black weights from Google Fonts",
"Reset default text margins and set section spacing deliberately". Start with a
verb, describe the change, no period, no prefix.

Usually one commit per lesson. Several is fine if they are distinct steps.

## 3. Publish

```
git push -u origin <short-slug>
```
Send the branch up. `-u` links it so later pushes are plain `git push`.

```
gh pr create --title "<lesson title>" --body "Closes #<issue-number>"
```
Open the PR. "Closes #N" makes GitHub close the issue when the PR merges.

```
gh pr merge --merge --delete-branch
```
Merge with a merge commit (keeps the branch visible in history), delete the branch
on GitHub and locally, and switch back to `main`.

```
git pull --ff-only origin main
```
Bring the merge commit down so `main` matches GitHub. Now you are ready for step 1
of the next lesson.

## 4. Where am I?

```
git status -sb
```
Current branch, what's staged, what's modified, and whether you are ahead of or
behind GitHub.

```
git log --oneline --graph -10
```
Recent history as a tree. Merge commits show the PR number.

```
gh pr status
gh issue list
```
Open PRs for this branch and open issues.

## 5. Fixing common mistakes

**Started editing while still on `main`.** Nothing is lost. Create the branch now;
uncommitted changes come with you:
```
git switch -c <short-slug>
```

**Typo in the last commit message, not pushed yet:**
```
git commit --amend -m "<corrected message>"
```

**Forgot a file in the last commit, not pushed yet:**
```
git add <file>
git commit --amend --no-edit
```

**Pushed, then made another change on the same branch.** Just commit and
`git push` again. The PR updates itself.

**Local list of remote branches is stale** (shows branches already deleted on GitHub):
```
git fetch --prune
```
portfolio-css has seven of these left over. Harmless, but this cleans them.

**`git pull --ff-only` refused.** `main` has local commits GitHub doesn't, or the
reverse with a conflict. Run `git status -sb` and `git log --oneline -5`, then ask
before doing anything else. Do not use `--force`.

**Want to see what a past lesson changed:**
```
git show <commit-hash>
```
Or `gh pr view <number> --web` to read it on GitHub.
