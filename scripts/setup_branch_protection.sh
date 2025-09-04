#!/bin/bash
# GitHub Branch Protection Setup Script
# Run this script to configure branch protection rules

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔐 Setting up GitHub Branch Protection Rules${NC}"
echo "This script will guide you through configuring branch protection for Railway deployment control."
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed.${NC}"
    echo "Please install GitHub CLI first:"
    echo "  - macOS: brew install gh"
    echo "  - Ubuntu: sudo apt install gh"
    echo "  - Or visit: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}🔑 You need to authenticate with GitHub first.${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Get repository information
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login')
REPO_NAME=$(gh repo view --json name --jq '.name')

echo -e "${GREEN}📋 Repository: ${REPO_OWNER}/${REPO_NAME}${NC}"
echo ""

# Function to create branch protection rule
create_branch_protection() {
    local branch=$1
    local description=$2
    
    echo -e "${YELLOW}🛡️  Setting up protection for ${branch} branch (${description})${NC}"
    
    # Create branch protection rule
    gh api repos/${REPO_OWNER}/${REPO_NAME}/branches/${branch}/protection \
        --method PUT \
        --field required_status_checks='{"strict":true,"contexts":[]}' \
        --field enforce_admins=true \
        --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":false}' \
        --field restrictions=null \
        --field allow_force_pushes=false \
        --field allow_deletions=false \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Branch protection enabled for ${branch}${NC}"
    else
        echo -e "${RED}❌ Failed to set protection for ${branch}${NC}"
        echo "This might be because:"
        echo "  - You don't have admin permissions on the repository"
        echo "  - The branch doesn't exist yet"
        echo "  - GitHub API rate limits"
    fi
}

# Create main branch protection (Production)
echo -e "${GREEN}Setting up main branch protection (Production deployment control)${NC}"
create_branch_protection "main" "Production deployment"

echo ""

# Create staging branch protection (Optional)
echo -e "${YELLOW}Do you want to protect the staging branch too? (y/n)${NC}"
read -r setup_staging

if [[ $setup_staging =~ ^[Yy]$ ]]; then
    create_branch_protection "staging" "Staging deployment"
fi

echo ""

# Create development branch if it doesn't exist
echo -e "${GREEN}Ensuring development branch exists...${NC}"
git show-ref --verify --quiet refs/heads/development
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Development branch already exists${NC}"
else
    echo -e "${YELLOW}📝 Creating development branch...${NC}"
    git checkout -b development 2>/dev/null || git checkout development
    git push -u origin development
fi

echo ""

# Push staging branch if it doesn't exist on remote
echo -e "${GREEN}Ensuring staging branch exists on remote...${NC}"
if git ls-remote --heads origin staging | grep -q staging; then
    echo -e "${GREEN}✅ Staging branch already exists on remote${NC}"
else
    echo -e "${YELLOW}📝 Pushing staging branch to remote...${NC}"
    git push -u origin staging
fi

echo ""

# Set default branch to development
echo -e "${YELLOW}Do you want to set 'development' as the default branch for new PRs? (y/n)${NC}"
read -r set_default

if [[ $set_default =~ ^[Yy]$ ]]; then
    gh api repos/${REPO_OWNER}/${REPO_NAME} \
        --method PATCH \
        --field default_branch='development' \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Default branch set to development${NC}"
    else
        echo -e "${RED}❌ Failed to set default branch${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 Branch protection setup complete!${NC}"
echo ""
echo -e "${YELLOW}Summary of your deployment control setup:${NC}"
echo "📦 main branch    → Protected, auto-deploys to Railway production"
echo "🧪 staging branch → ${setup_staging:+Protected, }deploys to Railway staging"
echo "🛠️  development   → Unprotected, no automatic deployment"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Configure Railway to deploy only from 'main' branch"
echo "2. Optionally create staging Railway service for 'staging' branch"
echo "3. Always work on 'development' branch for new features"
echo "4. Use Pull Requests to merge: development → staging → main"
echo ""
echo -e "${YELLOW}To complete Railway configuration:${NC}"
echo "1. Go to your Railway dashboard"
echo "2. In your service settings, set 'Source Repo' branch to 'main'"
echo "3. Enable 'Auto Deploy' only for the main branch"
echo "4. For staging, create a separate service connected to 'staging' branch"