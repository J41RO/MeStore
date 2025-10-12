#!/bin/bash
# 🚨 GIT CONTROL AI - VALIDATION PROTOCOL
# Author: git-control-ai
# Purpose: Automated validation of reorganization operations

set -e

echo "🔍 GIT CONTROL AI - VALIDATION PROTOCOL"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VALIDATION_LOG="/home/admin-jairo/MeStore/.workspace/departments/infrastructure/git-control-ai/logs/validation_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$VALIDATION_LOG")"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$VALIDATION_LOG"
}

error() {
    echo -e "${RED}❌ ERROR: $1${NC}" | tee -a "$VALIDATION_LOG"
}

warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}" | tee -a "$VALIDATION_LOG"
}

success() {
    echo -e "${GREEN}✅ SUCCESS: $1${NC}" | tee -a "$VALIDATION_LOG"
}

log "Starting Git Control validation protocol"

# 1. VERIFY GIT MV USAGE (NO PLAIN MV)
echo ""
echo "📋 1. VALIDATING GIT MV USAGE..."
echo "================================"

# Check recent commits for renames
RECENT_RENAMES=$(git log --name-status --oneline -20 | grep "^R" || true)

if [ -z "$RECENT_RENAMES" ]; then
    warning "No git mv operations detected in last 20 commits"
else
    success "Found git mv operations:"
    echo "$RECENT_RENAMES" | head -10
    log "Git mv operations found: $(echo "$RECENT_RENAMES" | wc -l) files"
fi

# 2. VERIFY PROTECTED FILES
echo ""
echo "📋 2. VALIDATING PROTECTED FILES..."
echo "==================================="

PROTECTED_FILES=("CLAUDE.md" "README.md" "app/main.py" "docker-compose.yml" "app/api/v1/deps/auth.py" "app/models/user.py")
PROTECTED_VIOLATIONS=0

for file in "${PROTECTED_FILES[@]}"; do
    if git diff --cached --name-only | grep -q "^$file$"; then
        error "Protected file in staging: $file"
        PROTECTED_VIOLATIONS=$((PROTECTED_VIOLATIONS + 1))
    fi
done

if [ $PROTECTED_VIOLATIONS -eq 0 ]; then
    success "No protected files in staging area"
else
    error "Found $PROTECTED_VIOLATIONS protected file violations"
fi

# 3. VERIFY COMMIT FORMAT
echo ""
echo "📋 3. VALIDATING COMMIT FORMAT..."
echo "================================="

LAST_COMMIT_MSG=$(git log -1 --pretty=format:"%s")
if echo "$LAST_COMMIT_MSG" | grep -qE "^(feat|fix|docs|refactor|chore|test|style)\(.*\):"; then
    success "Last commit follows conventional format: $LAST_COMMIT_MSG"
else
    warning "Last commit may not follow format: $LAST_COMMIT_MSG"
fi

# 4. VERIFY REPOSITORY INTEGRITY
echo ""
echo "📋 4. VALIDATING REPOSITORY INTEGRITY..."
echo "========================================"

if git fsck --no-progress > /dev/null 2>&1; then
    success "Repository integrity verified (git fsck passed)"
else
    error "Repository integrity check failed"
fi

# 5. CHECK FOR LOST FILES
echo ""
echo "📋 5. CHECKING FOR LOST FILES..."
echo "================================"

DELETED_FILES=$(git status --porcelain | grep "^D" | wc -l)
if [ "$DELETED_FILES" -gt 0 ]; then
    warning "Found $DELETED_FILES deleted files (verify these are intentional)"
    git status --porcelain | grep "^D" | head -10
else
    success "No deleted files detected"
fi

# 6. VERIFY REPOSITORY SIZE
echo ""
echo "📋 6. CHECKING REPOSITORY SIZE..."
echo "================================="

REPO_SIZE=$(du -sh .git/ | cut -f1)
log "Current repository size: $REPO_SIZE"
echo "Repository size: $REPO_SIZE"

# 7. HISTORY PRESERVATION SAMPLE
echo ""
echo "📋 7. VERIFYING HISTORY PRESERVATION (SAMPLE)..."
echo "================================================="

# Sample a few key files to verify history
SAMPLE_FILES=(
    "docs/guides/setup/DATABASE_SETUP.md"
    "docs/architecture/WOMPI_INTEGRATION_FLOW_DIAGRAM.md"
    "docs/executive/MVP_EXECUTIVE_SUMMARY.md"
)

for file in "${SAMPLE_FILES[@]}"; do
    if [ -f "$file" ]; then
        COMMITS=$(git log --follow --oneline "$file" | wc -l)
        if [ "$COMMITS" -gt 0 ]; then
            success "History preserved for $file ($COMMITS commits)"
        else
            warning "No history found for $file"
        fi
    fi
done

# 8. GENERATE SUMMARY
echo ""
echo "📊 VALIDATION SUMMARY"
echo "====================="
echo ""

TOTAL_STAGED=$(git diff --cached --name-only | wc -l)
TOTAL_MODIFIED=$(git status --porcelain | grep "^M" | wc -l)
TOTAL_UNTRACKED=$(git status --porcelain | grep "^??" | wc -l)

echo "Staged files: $TOTAL_STAGED"
echo "Modified files: $TOTAL_MODIFIED"
echo "Untracked files: $TOTAL_UNTRACKED"
echo "Protected violations: $PROTECTED_VIOLATIONS"
echo ""

if [ $PROTECTED_VIOLATIONS -eq 0 ]; then
    success "Validation passed - Ready to proceed"
    log "Validation completed successfully"
    exit 0
else
    error "Validation failed - Address protected file violations"
    log "Validation failed with $PROTECTED_VIOLATIONS violations"
    exit 1
fi
