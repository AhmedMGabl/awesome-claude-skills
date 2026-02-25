---
name: git-workflows
description: Git workflows and advanced operations covering branching strategies (Gitflow, trunk-based, GitHub Flow), interactive rebase, cherry-picking, bisect for debugging, stashing, worktrees, hooks, submodules, conflict resolution, and commit message conventions.
---

# Git Workflows

This skill should be used when managing Git workflows and performing advanced Git operations. It covers branching strategies, rebasing, hooks, worktrees, and team conventions.

## When to Use This Skill

Use this skill when you need to:

- Choose a branching strategy for a team
- Perform interactive rebases or cherry-picks
- Set up Git hooks for quality gates
- Debug issues with git bisect
- Manage complex merge/conflict scenarios

## Branching Strategies

```
STRATEGY          WHEN TO USE              BRANCHES
────────────────────────────────────────────────────────
Trunk-based       CI/CD, small teams       main + short-lived feature
GitHub Flow       Open source, SaaS        main + feature PRs
Gitflow           Scheduled releases       main, develop, feature, release, hotfix
```

## Conventional Commits

```
TYPE       DESCRIPTION                EXAMPLE
──────────────────────────────────────────────────
feat       New feature                feat: add user search
fix        Bug fix                    fix: prevent crash on empty input
docs       Documentation              docs: update API reference
refactor   Code restructure           refactor: extract auth middleware
test       Add/update tests           test: add login flow tests
chore      Build/tooling              chore: update dependencies
perf       Performance                perf: cache database queries
ci         CI/CD changes              ci: add e2e test step
```

## Interactive Rebase

```bash
# Rebase last 5 commits
git rebase -i HEAD~5

# Commands in the editor:
# pick   — keep commit as-is
# reword — change commit message
# squash — merge into previous commit
# fixup  — merge into previous, discard message
# drop   — remove commit

# Rebase onto main before merging
git fetch origin
git rebase origin/main
```

## Cherry-Pick

```bash
# Apply specific commit to current branch
git cherry-pick abc1234

# Cherry-pick without committing
git cherry-pick --no-commit abc1234

# Cherry-pick a range
git cherry-pick abc1234..def5678
```

## Git Bisect

```bash
# Find which commit introduced a bug
git bisect start
git bisect bad
git bisect good v1.0.0

# Test each checkout, then:
git bisect good   # or git bisect bad
# Repeat until found
git bisect reset

# Automated bisect
git bisect start HEAD v1.0.0
git bisect run npm test
```

## Stashing

```bash
git stash push -m "WIP: feature work"
git stash list
git stash apply           # Keep in stash list
git stash pop             # Apply and remove
git stash push -u -m "with untracked"
```

## Git Worktrees

```bash
git worktree add ../hotfix-branch hotfix/critical-bug
git worktree list
git worktree remove ../hotfix-branch
```

## Git Hooks (Husky + lint-staged)

```bash
#!/bin/sh
# .husky/pre-commit
npx lint-staged

# .husky/commit-msg
npx commitlint --edit $1
```

```json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md}": ["prettier --write"]
  }
}
```

## Conflict Resolution

```bash
# See conflicted files
git diff --name-only --diff-filter=U

# Accept theirs or ours
git checkout --theirs path/to/file
git checkout --ours path/to/file

# Abort
git merge --abort
git rebase --abort
```

## Useful Aliases

```bash
[alias]
  lg = log --oneline --graph --decorate -20
  unstage = reset HEAD --
  amend = commit --amend --no-edit
  undo = reset --soft HEAD~1
```

## Additional Resources

- Pro Git book: https://git-scm.com/book
- Conventional Commits: https://www.conventionalcommits.org/
- Gitflow: https://nvie.com/posts/a-successful-git-branching-model/
