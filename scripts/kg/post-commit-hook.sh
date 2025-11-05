#!/bin/bash
# Git post-commit hook for auto-updating knowledge graph
# Install: cp scripts/kg/post-commit-hook.sh .git/hooks/post-commit && chmod +x .git/hooks/post-commit

COMMIT_MSG=$(git log -1 --pretty=%B)
COMMIT_DATE=$(date +%Y-%m-%d)
FILES_CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD | wc -l)

# Parse commit type (conventional commits)
if [[ $COMMIT_MSG =~ ^feat: ]]; then
    echo "KG Update: New feature detected"
    # TODO: Update entity with feature observation
elif [[ $COMMIT_MSG =~ ^fix: ]]; then
    echo "KG Update: Bug fix detected"
elif [[ $COMMIT_MSG =~ ^perf: ]]; then
    echo "KG Update: Performance improvement detected"
elif [[ $COMMIT_MSG =~ ^refactor: ]]; then
    echo "KG Update: Refactor detected - $FILES_CHANGED files changed"
elif [[ $COMMIT_MSG =~ ^test: ]]; then
    echo "KG Update: Test changes detected"
    # Run test parser
    if [ -f "scripts/kg/test-result-parser.py" ]; then
        pytest tests/ --tb=no -q > /tmp/test-output.txt 2>&1
        python scripts/kg/test-result-parser.py /tmp/test-output.txt
    fi
fi

# Track significant changes
if [ $FILES_CHANGED -gt 10 ]; then
    echo "KG Update: Major changes detected ($FILES_CHANGED files)"
fi

echo "KG Hook: Commit processed at $COMMIT_DATE"
