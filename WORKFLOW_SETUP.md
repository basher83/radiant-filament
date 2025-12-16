# CI Workflow Setup

This directory contains scripts to set up the GitHub Actions CI workflow for this repository.

## Quick Setup

Run ONE of the following commands from the repository root:

### Option 1: Using Python (Recommended)
```bash
python create_workflow.py
```

### Option 2: Using Shell Script
```bash
bash setup-workflow.sh
```

### Option 3: Manual Setup
1. Create the directory:
   ```bash
   mkdir -p .github/workflows
   ```

2. Create the file `.github/workflows/fast-pr-gate.yml` with the content from `docs/workflow-fast-pr-gate.md`

## What Gets Created

The workflow file `.github/workflows/fast-pr-gate.yml` will be created with the following features:

- **Triggers**: Runs on pull requests to the `main` branch
- **Permissions**: Minimal (`contents: read`)
- **Concurrency**: Cancels in-progress runs when new commits are pushed
- **Steps**:
  1. Checkout code
  2. Setup mise (installs Python 3.13, uv, ruff, etc.)
  3. Detect available mise tasks and tools
  4. Install dependencies with `uv sync`
  5. Run linting with `mise run lint` (if available)
  6. Check formatting with `mise run format-check` (if available)
  7. Run tests with pytest

## Design Decisions

- Uses `jdx/mise-action@v3` with `github_token` to avoid API rate limits
- Conditionally runs steps only if the corresponding tools/tasks exist
- Designed to be portable across repositories
- Fast and minimal (single job, no unnecessary complexity)
- Follows the repository's existing conventions (mise, uv, ruff, pytest)

## After Running

Once the workflow is created:
1. Review the file: `.github/workflows/fast-pr-gate.yml`
2. Commit it: `git add .github/workflows/fast-pr-gate.yml && git commit -m "Add CI workflow"`
3. Push: `git push`
4. The workflow will automatically run on future PRs

## Detected Configuration

From analyzing the repository:
- **Build tool**: mise with Python 3.13, uv 0.9.13
- **Linting**: ruff 0.14.7 via `mise run lint`
- **Formatting**: ruff via `mise run format-check`
- **Testing**: pytest 9.0.2+
- **Dependencies**: uv (package mode enabled)
- **Mise tasks found**: lint, lint-fix, format, format-check, pre-commit-run

## Notes

- The workflow assumes `main` as the default branch. If your default branch is different, edit the workflow file.
- The workflow will skip steps for tasks that don't exist, making it safe to use even if the repository configuration changes.
