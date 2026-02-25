---
name: git-workflows
description: Git workflows covering branching strategies (GitFlow, trunk-based), merge vs rebase, conflict resolution, interactive rebase, cherry-pick, bisect, worktrees, hooks, monorepo management, and team collaboration patterns.
---

# Git Workflows

This skill should be used when managing Git repositories, resolving conflicts, choosing branching strategies, or implementing team collaboration workflows. It covers branching models, advanced Git commands, hooks, and monorepo patterns.

## When to Use This Skill

Use this skill when you need to:

- Choose between GitFlow, trunk-based, or GitHub Flow
- Resolve merge conflicts and rebase issues
- Use advanced Git features (bisect, cherry-pick, worktrees)
- Set up Git hooks for automation
- Manage monorepos with multiple projects
- Implement code review and PR workflows
- Clean up Git history

## Branching Strategies

### GitHub Flow (Recommended for most teams)

```bash
# Simple: main + feature branches
# 1. Create feature branch
git checkout -b feature/user-auth

# 2. Make commits
git add . && git commit -m "feat: add login endpoint"

# 3. Push and create PR
git push -u origin feature/user-auth
gh pr create --title "Add user authentication"

# 4. After review, merge to main (squash or merge commit)
gh pr merge --squash

# 5. Deploy main automatically
```

### Trunk-Based Development

```bash
# Very short-lived branches (< 1 day), direct to main
git checkout -b fix/typo-header

# Small, focused changes
git commit -m "fix: correct header typo"
git push -u origin fix/typo-header

# Merge quickly (no long-lived branches)
gh pr create --title "Fix header typo" && gh pr merge --squash

# Feature flags for incomplete features
# if (featureFlags.newDashboard) { showNewDashboard() }
```

### GitFlow (For release-based projects)

```bash
# Long-lived branches: main, develop
# Short-lived: feature/*, release/*, hotfix/*

# Feature
git checkout -b feature/new-ui develop
# ... work ...
git checkout develop && git merge --no-ff feature/new-ui

# Release
git checkout -b release/1.2.0 develop
# ... version bump, final fixes ...
git checkout main && git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release 1.2.0"
git checkout develop && git merge --no-ff release/1.2.0

# Hotfix
git checkout -b hotfix/1.2.1 main
# ... fix ...
git checkout main && git merge --no-ff hotfix/1.2.1
git tag -a v1.2.1 -m "Hotfix 1.2.1"
git checkout develop && git merge --no-ff hotfix/1.2.1
```

## Merge vs Rebase

### When to Rebase

```bash
# Update feature branch with latest main (cleaner history)
git checkout feature/my-feature
git fetch origin
git rebase origin/main

# If conflicts occur during rebase:
# 1. Fix conflicts in files
# 2. Stage resolved files
git add <resolved-files>
# 3. Continue rebase
git rebase --continue
# Or abort if stuck
git rebase --abort

# Force push after rebase (only for personal branches!)
git push --force-with-lease  # Safer than --force
```

### When to Merge

```bash
# Merge main into feature (preserves history)
git checkout feature/my-feature
git merge main

# Merge strategies for PRs:
# Squash merge - clean main history, one commit per feature
gh pr merge --squash

# Merge commit - preserves full branch history
gh pr merge --merge

# Rebase merge - linear history without merge commits
gh pr merge --rebase
```

## Interactive Rebase

```bash
# Clean up last N commits before pushing
git rebase -i HEAD~5

# Commands in the editor:
# pick   abc1234 feat: add user model        (keep as-is)
# squash def5678 fix: typo in model           (merge into previous)
# reword ghi9012 WIP: working on auth         (change commit message)
# edit   jkl3456 feat: add auth middleware     (stop to amend)
# drop   mno7890 debug: temporary logging      (remove commit)
# fixup  pqr1234 fix: another typo            (merge, discard message)

# Reorder commits by moving lines

# After interactive rebase, force push to update remote
git push --force-with-lease
```

## Conflict Resolution

```bash
# Standard merge conflict markers:
# <<<<<<< HEAD (your changes)
# Your code here
# =======
# Their code here
# >>>>>>> feature/other-branch

# Using merge tools
git mergetool  # Opens configured tool

# Accept one side entirely
git checkout --ours <file>     # Keep your version
git checkout --theirs <file>   # Keep their version

# After resolving all conflicts
git add <resolved-files>
git commit  # or git rebase --continue

# Rerere (Reuse Recorded Resolution)
git config rerere.enabled true
# Git remembers how you resolved conflicts and applies them automatically
```

## Advanced Commands

### Cherry-Pick

```bash
# Apply specific commits from another branch
git cherry-pick abc1234

# Cherry-pick without committing (stage only)
git cherry-pick --no-commit abc1234

# Cherry-pick a range
git cherry-pick abc1234..def5678

# If conflicts:
git cherry-pick --continue  # after resolving
git cherry-pick --abort     # to cancel
```

### Bisect (Find Bug-Introducing Commit)

```bash
# Binary search through commits
git bisect start
git bisect bad                 # Current commit is broken
git bisect good v1.0.0         # Last known good commit

# Git checks out middle commit - test and mark:
git bisect good  # if this commit works
git bisect bad   # if this commit is broken

# Git narrows down and finds the culprit
# Result: abc1234 is the first bad commit

git bisect reset  # Return to original branch

# Automated bisect with test script
git bisect start HEAD v1.0.0
git bisect run npm test
```

### Worktrees

```bash
# Work on multiple branches simultaneously
git worktree add ../my-project-hotfix hotfix/critical-bug
cd ../my-project-hotfix
# Fix bug, commit, push - without switching branches in main worktree

# List worktrees
git worktree list

# Remove when done
git worktree remove ../my-project-hotfix
```

### Stash

```bash
# Save work in progress
git stash
git stash push -m "WIP: refactoring auth"

# Include untracked files
git stash push -u -m "WIP with new files"

# List stashes
git stash list

# Apply and remove
git stash pop        # Apply most recent and remove from stash
git stash apply      # Apply but keep in stash
git stash pop stash@{2}  # Apply specific stash

# Create branch from stash
git stash branch new-feature stash@{0}

# Clear all stashes
git stash clear
```

## Git Hooks

```bash
# .husky/pre-commit (using husky)
#!/bin/sh
npx lint-staged

# .husky/commit-msg
#!/bin/sh
npx commitlint --edit "$1"

# package.json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md}": ["prettier --write"]
  },
  "commitlint": {
    "extends": ["@commitlint/config-conventional"]
  }
}

# Install hooks
npx husky init
```

### Conventional Commits

```bash
# Format: <type>(<scope>): <description>
feat(auth): add OAuth2 login flow
fix(api): handle null response from payment gateway
docs(readme): add deployment instructions
refactor(db): extract query builder into separate module
test(users): add integration tests for user service
chore(deps): update dependencies to latest versions
perf(search): add index for full-text queries
ci(actions): add caching to CI pipeline

# Breaking changes
feat(api)!: change authentication from cookies to JWT
# or
feat(api): change auth method

BREAKING CHANGE: API now requires Bearer token instead of cookies
```

## History Management

```bash
# View history
git log --oneline --graph --all    # Visual branch graph
git log --author="name" --since="1 week ago"
git log --stat                      # Files changed per commit
git log -p -- path/to/file         # Full diff for specific file
git log --follow path/to/file      # Track file through renames

# Find who changed what
git blame path/to/file
git blame -L 10,20 path/to/file   # Specific lines

# Search commits
git log --grep="fix login"          # Search commit messages
git log -S "functionName"           # Search for code changes (pickaxe)
git log -G "regex_pattern"          # Regex search in diffs

# Undo commits
git reset --soft HEAD~1            # Undo commit, keep changes staged
git reset --mixed HEAD~1           # Undo commit, keep changes unstaged
git revert abc1234                 # Create new commit that undoes changes (safe)

# Recover lost commits
git reflog                          # Shows all recent HEAD movements
git checkout abc1234               # Recover specific commit
git branch recovered abc1234       # Create branch at lost commit
```

## Monorepo Management

```bash
# Sparse checkout (clone only what you need)
git clone --filter=blob:none --sparse <repo-url>
cd repo
git sparse-checkout set packages/my-package shared/

# Partial clone (download blobs on demand)
git clone --filter=blob:none <repo-url>

# Git submodules
git submodule add <repo-url> libs/my-lib
git submodule update --init --recursive

# Useful aliases for monorepos
git config alias.ls "log --oneline -20"
git config alias.graph "log --oneline --graph --all -20"
git config alias.recent "branch --sort=-committerdate --format='%(committerdate:short) %(refname:short)'"
```

## Configuration

```bash
# Essential Git config
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global pull.rebase true          # Rebase on pull
git config --global fetch.prune true          # Auto-prune deleted remotes
git config --global rerere.enabled true       # Remember conflict resolutions
git config --global diff.algorithm histogram  # Better diffs
git config --global merge.conflictstyle diff3 # Show base in conflicts

# Useful aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.st status
git config --global alias.cm "commit -m"
git config --global alias.unstage "reset HEAD --"
git config --global alias.last "log -1 HEAD"
git config --global alias.visual "log --oneline --graph --all"
```

## Additional Resources

- Pro Git Book: https://git-scm.com/book
- Git documentation: https://git-scm.com/docs
- Conventional Commits: https://www.conventionalcommits.org/
- GitHub Flow: https://docs.github.com/en/get-started/quickstart/github-flow
- Husky: https://typicode.github.io/husky/
