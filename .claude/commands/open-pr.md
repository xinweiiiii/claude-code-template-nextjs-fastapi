Open a pull request for the current branch using the `pr-writer` subagent.

1. Use the `pr-writer` subagent on the current branch. Ask it to:
   - Run `git log main..HEAD --oneline` and `git diff main...HEAD` to understand all changes
   - Write a PR description with four sections: Problem, Solution, Deployment, Testing
   - Open the PR against `main` using `gh pr create`

2. Return the PR URL when done.
