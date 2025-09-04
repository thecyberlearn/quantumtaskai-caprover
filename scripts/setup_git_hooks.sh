#!/bin/bash
# Setup Git Hooks for Auto-Documentation Updates

PROJECT_ROOT=$(pwd)
GIT_HOOKS_DIR="$PROJECT_ROOT/.git/hooks"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

echo "Setting up git hooks for auto-documentation updates..."

# Create post-commit hook
cat > "$GIT_HOOKS_DIR/post-commit" << 'EOF'
#!/bin/bash
# Auto-update documentation after successful commits

PROJECT_ROOT=$(git rev-parse --show-toplevel)
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
AUTO_UPDATE_SCRIPT="$SCRIPTS_DIR/auto_update_docs.py"

# Check if the auto-update script exists
if [ -f "$AUTO_UPDATE_SCRIPT" ]; then
    echo "Auto-updating documentation after commit..."
    python3 "$AUTO_UPDATE_SCRIPT" "$PROJECT_ROOT"
    
    # Check if any documentation was updated
    if [ -f "$PROJECT_ROOT/docs_update_summary.txt" ]; then
        echo "Documentation auto-update completed. Check docs_update_summary.txt for details."
        
        # Optionally auto-commit documentation updates
        # Uncomment the lines below if you want documentation updates to be auto-committed
        # git add *.md docs/ CLAUDE.md README.md docs_update_summary.txt
        # git commit -m "📚 Auto-update documentation after recent changes"
    fi
else
    echo "Auto-update script not found at $AUTO_UPDATE_SCRIPT"
fi
EOF

# Make post-commit hook executable
chmod +x "$GIT_HOOKS_DIR/post-commit"

# Create pre-push hook to ensure documentation is up to date
cat > "$GIT_HOOKS_DIR/pre-push" << 'EOF'
#!/bin/bash
# Ensure documentation is up to date before pushing

PROJECT_ROOT=$(git rev-parse --show-toplevel)
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
AUTO_UPDATE_SCRIPT="$SCRIPTS_DIR/auto_update_docs.py"

echo "Checking documentation status before push..."

# Run documentation update check
if [ -f "$AUTO_UPDATE_SCRIPT" ]; then
    python3 "$AUTO_UPDATE_SCRIPT" "$PROJECT_ROOT"
    
    # Check if any updates were made
    if git diff --quiet; then
        echo "Documentation is up to date."
    else
        echo "Documentation updates were generated. Please review and commit them before pushing."
        echo "Modified files:"
        git diff --name-only
        echo ""
        echo "To commit documentation updates:"
        echo "  git add ."
        echo "  git commit -m '📚 Update documentation'"
        echo "  git push"
        
        # Uncomment to block push until docs are committed
        # exit 1
    fi
else
    echo "Auto-update script not found. Proceeding with push..."
fi
EOF

# Make pre-push hook executable
chmod +x "$GIT_HOOKS_DIR/pre-push"

# Create a manual trigger script
cat > "$SCRIPTS_DIR/update_docs_manual.sh" << 'EOF'
#!/bin/bash
# Manual trigger for documentation updates

PROJECT_ROOT=$(git rev-parse --show-toplevel)
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
AUTO_UPDATE_SCRIPT="$SCRIPTS_DIR/auto_update_docs.py"

echo "Manually triggering documentation update..."

if [ -f "$AUTO_UPDATE_SCRIPT" ]; then
    python3 "$AUTO_UPDATE_SCRIPT" "$PROJECT_ROOT"
    
    if [ -f "$PROJECT_ROOT/docs_update_summary.txt" ]; then
        echo ""
        echo "Documentation update completed!"
        echo "Summary saved to: docs_update_summary.txt"
        echo ""
        echo "To commit the updates:"
        echo "  git add ."
        echo "  git commit -m '📚 Manual documentation update'"
    fi
else
    echo "Error: Auto-update script not found at $AUTO_UPDATE_SCRIPT"
    exit 1
fi
EOF

chmod +x "$SCRIPTS_DIR/update_docs_manual.sh"

echo "Git hooks setup completed!"
echo ""
echo "Created hooks:"
echo "  - post-commit: Auto-updates docs after each commit"
echo "  - pre-push: Checks docs before pushing"
echo ""
echo "Created scripts:"
echo "  - $SCRIPTS_DIR/update_docs_manual.sh: Manual documentation update trigger"
echo ""
echo "To disable auto-updates, remove or rename the hooks in .git/hooks/"