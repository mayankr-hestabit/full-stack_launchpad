# Merge Conflict Postmortem — Day 3

## Scenario
Two developers (clone-a and clone-b) cloned the same repository
and independently edited the same line in day3/calculator.js.

## What Happened
- clone-a added comment: "add function handles positive and negative numbers"
- clone-b added comment: "add function used by all arithmetic operations"
- clone-a pushed first successfully
- clone-b push was rejected (remote had new commits)
- clone-b ran `git pull --no-rebase origin master`
- Git detected both changes touched the same line → CONFLICT

## Conflict Markers Seen
<<<<<<< HEAD
// Developer B: add function used by all arithmetic operations
=======
// Developer A: add function handles positive and negative numbers
>>>>>>> refs/remotes/origin/master

## Resolution
Manually edited the file to keep BOTH comments, removed conflict
markers, then:
  git add day3/calculator.js
  git commit -m "Day3: resolve merge conflict keeping both developer comments"
  git push origin master

## Key Lessons
- Git cannot auto-merge when two people edit the exact same line
- Always pull before starting new work to minimize conflicts
- Conflict markers show exactly what each side changed
- Resolution is always manual — you decide what the final code looks like
- `git pull --no-rebase` creates a merge commit, preserving full history
