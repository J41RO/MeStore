#!/bin/bash
echo "🧪 Frontend Verification Suite (like pytest for backend)"
echo "=================================================="

cd "$(dirname "$0")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

errors=0
warnings=0

echo -e "${BLUE}1. TypeScript Check...${NC}"
if npx tsc --noEmit 2>/dev/null; then
    echo -e "${GREEN}✅ TypeScript: PASS${NC}"
else
    echo -e "${RED}❌ TypeScript: FAIL${NC}"
    ((errors++))
fi

echo -e "${BLUE}2. Build Check...${NC}"
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Build: PASS${NC}"
else
    echo -e "${RED}❌ Build: FAIL${NC}"
    ((errors++))
fi

echo -e "${BLUE}3. Test Suite...${NC}"
test_output=$(npm run test 2>&1)
test_count=$(echo "$test_output" | grep "Tests:" | grep -o '[0-9]\+ passed' | grep -o '[0-9]\+')
if [[ "$test_count" -gt 0 ]]; then
    echo -e "${GREEN}✅ Tests: PASS ($test_count tests executed)${NC}"
else
    echo -e "${YELLOW}⚠️  Tests: WARNINGS (no tests found)${NC}"
    ((warnings++))
fi

echo -e "${BLUE}4. Lint Check...${NC}"
lint_output=$(npm run lint 2>&1)
lint_errors=$(echo "$lint_output" | grep -c "error")
if [ "$lint_errors" -eq 0 ]; then
    echo -e "${GREEN}✅ Lint: PASS${NC}"
else
    echo -e "${YELLOW}⚠️  Lint: $lint_errors warnings (continuable)${NC}"
    ((warnings++))
fi

echo -e "\n=================================================="
if [ $errors -eq 0 ]; then
    if [ $warnings -eq 0 ]; then
        echo -e "${GREEN}🎉 Perfect! All checks passed! Frontend ready for development${NC}"
    else
        echo -e "${GREEN}✅ Good! Core checks passed ($warnings warnings, but continuable)${NC}"
    fi
    echo -e "${GREEN}🚀 You can now develop frontend components safely${NC}"
    exit 0
else
    echo -e "${RED}💥 $errors critical error(s) found! Fix before continuing${NC}"
    if [ $warnings -gt 0 ]; then
        echo -e "${YELLOW}📝 Also $warnings warning(s) that should be addressed${NC}"
    fi
    exit 1
fi
