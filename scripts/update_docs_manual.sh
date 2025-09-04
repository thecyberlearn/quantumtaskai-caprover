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
