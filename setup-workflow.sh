#!/bin/bash
# Script to create the GitHub Actions workflow for fast PR gating

# Create the directory structure
mkdir -p .github/workflows

# Create the workflow file
cat > .github/workflows/fast-pr-gate.yml << 'EOF'
name: Fast PR Gate

on:
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: fast-pr-gate-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  fast-pr-gate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup mise
        uses: jdx/mise-action@v3
        with:
          install: true
          cache: true
          github_token: ${{ secrets.GITHUB_TOKEN }}

      - name: Detect mise tasks and tools
        id: detect
        run: |
          # Check for mise tasks
          if mise tasks --json 2>/dev/null | jq -e '.[] | select(.name == "lint")' >/dev/null; then
            echo "has_lint=true" >> $GITHUB_OUTPUT
          else
            echo "has_lint=false" >> $GITHUB_OUTPUT
          fi
          
          if mise tasks --json 2>/dev/null | jq -e '.[] | select(.name == "format-check")' >/dev/null; then
            echo "has_format_check=true" >> $GITHUB_OUTPUT
          else
            echo "has_format_check=false" >> $GITHUB_OUTPUT
          fi
          
          if mise tasks --json 2>/dev/null | jq -e '.[] | select(.name == "test" or .name == "tests")' >/dev/null; then
            echo "has_test=true" >> $GITHUB_OUTPUT
          else
            echo "has_test=false" >> $GITHUB_OUTPUT
          fi
          
          if mise tasks --json 2>/dev/null | jq -e '.[] | select(.name == "pre-commit-run")' >/dev/null; then
            echo "has_pre_commit=true" >> $GITHUB_OUTPUT
          else
            echo "has_pre_commit=false" >> $GITHUB_OUTPUT
          fi
          
          # Check for uv and pytest
          if command -v uv >/dev/null 2>&1; then
            echo "has_uv=true" >> $GITHUB_OUTPUT
          else
            echo "has_uv=false" >> $GITHUB_OUTPUT
          fi
          
          if command -v pytest >/dev/null 2>&1; then
            echo "has_pytest=true" >> $GITHUB_OUTPUT
          else
            echo "has_pytest=false" >> $GITHUB_OUTPUT
          fi

      - name: Install dependencies
        if: steps.detect.outputs.has_uv == 'true'
        run: uv sync

      - name: Run lint
        if: steps.detect.outputs.has_lint == 'true'
        run: mise run lint

      - name: Check formatting
        if: steps.detect.outputs.has_format_check == 'true'
        run: mise run format-check

      - name: Run tests
        if: steps.detect.outputs.has_test == 'true'
        run: mise run test

      - name: Run tests with pytest
        if: steps.detect.outputs.has_test == 'false' && steps.detect.outputs.has_pytest == 'true'
        run: uv run pytest
EOF

echo "Created .github/workflows/fast-pr-gate.yml"
echo "You can now commit this file to your repository."
