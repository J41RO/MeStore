#!/bin/bash

# TDD Test Runner Script for MeStore
# ==================================
# This script runs TDD tests with comprehensive coverage reporting
# and follows enterprise testing standards.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/admin-jairo/MeStore"
VENV_PATH="$PROJECT_ROOT/.venv"
TESTS_PATH="$PROJECT_ROOT/tests"
COVERAGE_MIN=75  # Minimum coverage percentage required
REPORTS_DIR="$PROJECT_ROOT/test-reports"

# Ensure we're in the project root
cd "$PROJECT_ROOT"

echo -e "${BLUE}🎯 TDD Test Runner for MeStore${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
    source "$VENV_PATH/bin/activate"
else
    echo -e "${RED}❌ Virtual environment not found at $VENV_PATH${NC}"
    exit 1
fi

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Function to run specific test categories
run_test_category() {
    local category=$1
    local description=$2
    local marker=$3

    echo -e "${BLUE}🔍 Running $description...${NC}"

    pytest \
        -m "$marker" \
        --tb=short \
        --durations=10 \
        --cov=app \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-report=xml:coverage.xml \
        --junitxml="$REPORTS_DIR/${category}_results.xml" \
        -v \
        || return 1

    echo -e "${GREEN}✅ $description completed successfully${NC}"
    echo ""
}

# Function to validate TDD compliance
validate_tdd_compliance() {
    echo -e "${BLUE}🔍 Validating TDD compliance...${NC}"

    # Check for RED-GREEN-REFACTOR patterns in test files
    tdd_test_files=$(find tests -name "*tdd*.py" | wc -l)

    if [ "$tdd_test_files" -gt 0 ]; then
        echo -e "${GREEN}✅ Found $tdd_test_files TDD test files${NC}"
    else
        echo -e "${RED}⚠️  No TDD test files found${NC}"
    fi

    # Check for proper test markers
    red_tests=$(grep -r "@red_test" tests/ | wc -l)
    green_tests=$(grep -r "@green_test" tests/ | wc -l)
    refactor_tests=$(grep -r "@refactor_test" tests/ | wc -l)

    echo -e "${BLUE}TDD Test Distribution:${NC}"
    echo -e "  RED phase tests: $red_tests"
    echo -e "  GREEN phase tests: $green_tests"
    echo -e "  REFACTOR phase tests: $refactor_tests"
    echo ""
}

# Function to check test coverage
check_coverage() {
    echo -e "${BLUE}📊 Checking test coverage...${NC}"

    # Run coverage report and capture percentage
    coverage_percentage=$(python -m coverage report --show-missing | grep TOTAL | awk '{print $4}' | sed 's/%//')

    if [ -z "$coverage_percentage" ]; then
        echo -e "${RED}❌ Could not determine coverage percentage${NC}"
        return 1
    fi

    echo -e "${BLUE}Current coverage: ${coverage_percentage}%${NC}"

    # Compare with minimum required coverage
    if [ "${coverage_percentage%.*}" -ge "$COVERAGE_MIN" ]; then
        echo -e "${GREEN}✅ Coverage meets minimum requirement (${COVERAGE_MIN}%)${NC}"
        return 0
    else
        echo -e "${RED}❌ Coverage below minimum requirement (${COVERAGE_MIN}%)${NC}"
        echo -e "${YELLOW}💡 Improve test coverage before deploying to production${NC}"
        return 1
    fi
}

# Function to run mutation testing (if available)
run_mutation_tests() {
    echo -e "${BLUE}🧬 Running mutation testing...${NC}"

    if command -v mutmut &> /dev/null; then
        mutmut run --paths-to-mutate=app/ --tests-dir=tests/ --runner="python -m pytest" || {
            echo -e "${YELLOW}⚠️  Mutation testing found issues${NC}"
            mutmut html
            echo -e "${BLUE}📊 Mutation report generated in htmlmut/index.html${NC}"
        }
    else
        echo -e "${YELLOW}⚠️  mutmut not installed, skipping mutation testing${NC}"
        echo -e "${BLUE}💡 Install with: pip install mutmut${NC}"
    fi
    echo ""
}

# Function to analyze test quality
analyze_test_quality() {
    echo -e "${BLUE}📈 Analyzing test quality...${NC}"

    # Count different types of tests
    unit_tests=$(find tests/unit -name "test_*.py" | wc -l)
    integration_tests=$(find tests/integration -name "test_*.py" | wc -l)
    tdd_tests=$(find tests -name "*tdd*.py" | wc -l)

    echo -e "${BLUE}Test Distribution:${NC}"
    echo -e "  Unit tests: $unit_tests"
    echo -e "  Integration tests: $integration_tests"
    echo -e "  TDD tests: $tdd_tests"

    # Check test to code ratio
    total_tests=$(find tests -name "test_*.py" | wc -l)
    total_source=$(find app -name "*.py" | wc -l)

    if [ "$total_source" -gt 0 ]; then
        test_ratio=$(echo "scale=2; $total_tests / $total_source" | bc -l)
        echo -e "  Test-to-code ratio: $test_ratio"

        if (( $(echo "$test_ratio >= 0.5" | bc -l) )); then
            echo -e "${GREEN}✅ Good test coverage ratio${NC}"
        else
            echo -e "${YELLOW}⚠️  Consider adding more tests${NC}"
        fi
    fi
    echo ""
}

# Main execution flow
main() {
    echo -e "${BLUE}Starting TDD test execution...${NC}"
    echo ""

    # Validate TDD compliance first
    validate_tdd_compliance

    # Set environment variables for testing
    export TESTING=1
    export DISABLE_SEARCH_SERVICE=1
    export DISABLE_CHROMA_SERVICE=1

    # Run different categories of tests
    echo -e "${BLUE}🧪 Running TDD test suite...${NC}"
    echo ""

    # 1. TDD Tests (highest priority)
    if ! run_test_category "tdd" "TDD Tests (RED-GREEN-REFACTOR)" "tdd"; then
        echo -e "${RED}❌ TDD tests failed! Fix before proceeding.${NC}"
        exit 1
    fi

    # 2. Unit Tests
    if ! run_test_category "unit" "Unit Tests" "unit"; then
        echo -e "${RED}❌ Unit tests failed!${NC}"
        exit 1
    fi

    # 3. Authentication Tests
    if ! run_test_category "auth" "Authentication Tests" "auth"; then
        echo -e "${RED}❌ Authentication tests failed!${NC}"
        exit 1
    fi

    # 4. Database Tests
    if ! run_test_category "database" "Database Tests" "database"; then
        echo -e "${YELLOW}⚠️  Some database tests failed, but continuing...${NC}"
    fi

    # 5. Integration Tests (if they exist and work)
    if [ -d "tests/integration" ] && [ "$(find tests/integration -name 'test_*.py' | wc -l)" -gt 0 ]; then
        if ! run_test_category "integration" "Integration Tests" "integration"; then
            echo -e "${YELLOW}⚠️  Some integration tests failed, but continuing...${NC}"
        fi
    fi

    # Check coverage requirements
    echo -e "${BLUE}📊 Analyzing test results...${NC}"
    check_coverage || {
        echo -e "${YELLOW}⚠️  Coverage below threshold, but tests passed${NC}"
    }

    # Additional quality checks
    analyze_test_quality

    # Mutation testing (optional)
    if [ "$1" = "--mutation" ]; then
        run_mutation_tests
    fi

    # Generate final report
    echo -e "${GREEN}🎉 TDD test execution completed!${NC}"
    echo -e "${BLUE}📋 Test Reports:${NC}"
    echo -e "  HTML Coverage: htmlcov/index.html"
    echo -e "  XML Coverage: coverage.xml"
    echo -e "  JUnit Results: $REPORTS_DIR/"
    echo ""

    # Summary
    echo -e "${GREEN}✅ All critical tests passed${NC}"
    echo -e "${BLUE}💡 Ready for TDD development cycle${NC}"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "TDD Test Runner for MeStore"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h      Show this help message"
        echo "  --mutation      Run mutation testing (requires mutmut)"
        echo "  --coverage-min  Set minimum coverage percentage (default: $COVERAGE_MIN)"
        echo "  --tdd-only      Run only TDD marked tests"
        echo "  --unit-only     Run only unit tests"
        echo "  --auth-only     Run only authentication tests"
        echo ""
        echo "Examples:"
        echo "  $0                  # Run full TDD test suite"
        echo "  $0 --mutation       # Run with mutation testing"
        echo "  $0 --tdd-only       # Run only TDD tests"
        ;;
    --mutation)
        main --mutation
        ;;
    --coverage-min)
        COVERAGE_MIN=$2
        main
        ;;
    --tdd-only)
        export TESTING=1
        export DISABLE_SEARCH_SERVICE=1
        export DISABLE_CHROMA_SERVICE=1
        run_test_category "tdd" "TDD Tests Only" "tdd"
        ;;
    --unit-only)
        export TESTING=1
        export DISABLE_SEARCH_SERVICE=1
        export DISABLE_CHROMA_SERVICE=1
        run_test_category "unit" "Unit Tests Only" "unit"
        ;;
    --auth-only)
        export TESTING=1
        export DISABLE_SEARCH_SERVICE=1
        export DISABLE_CHROMA_SERVICE=1
        run_test_category "auth" "Authentication Tests Only" "auth"
        ;;
    *)
        main "$@"
        ;;
esac