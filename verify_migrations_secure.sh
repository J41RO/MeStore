#!/bin/bash
set -euo pipefail  # Fail fast on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Environment validation
validate_environment() {
    log "=== 🔍 VALIDATING ENVIRONMENT ==="
    
    # Check if we're in the right directory
    if [[ ! -f "requirements.txt" ]] && [[ ! -f "pyproject.toml" ]] && [[ ! -f "setup.py" ]]; then
        error "Not in a Python project directory"
        exit 1
    fi
    
    # Check for required files
    local required_files=("tests/test_migrations_script.py" "alembic.ini")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            error "Required file not found: $file"
            exit 1
        fi
    done
    
    # Check for required commands
    local required_commands=("python" "alembic" "docker-compose")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Required command not found: $cmd"
            exit 1
        fi
    done
    
    log "✅ Environment validation passed"
}

# Test execution with error handling
run_tests() {
    log "=== 🧪 TESTING SCRIPTS MIGRACIONES ==="
    
    if ! python -m pytest tests/test_migrations_script.py -v --tb=short; then
        error "Tests failed - aborting verification"
        exit 1
    fi
    
    log "✅ Tests passed"
}

# Alembic verification
verify_alembic() {
    log "=== 🔗 VERIFICANDO ALEMBIC ==="
    
    # Check current revision
    if ! alembic current; then
        error "Alembic current command failed"
        exit 1
    fi
    
    # Check for pending migrations
    local check_output
    if check_output=$(alembic check 2>&1); then
        log "✅ No pending migrations"
    else
        warning "Pending migrations detected:"
        echo "$check_output"
    fi
}

# Docker validation
verify_docker() {
    log "=== 🐳 VERIFICANDO DOCKER ==="
    
    if [[ ! -f "docker-compose.yml" ]] && [[ ! -f "docker-compose.yaml" ]]; then
        warning "No docker-compose file found, skipping Docker verification"
        return 0
    fi
    
    if ! docker-compose config --quiet; then
        error "Docker Compose configuration is invalid"
        exit 1
    fi
    
    log "✅ Docker Compose configuration valid"
}

# Coverage report with validation
run_coverage() {
    log "=== 📊 COBERTURA ==="
    
    if ! python -m pytest --cov=scripts tests/test_migrations_script.py --cov-report=term-missing --cov-fail-under=40; then
        warning "Coverage below threshold or tests failed"
        return 1
    fi
    
    log "✅ Coverage report generated"
}

# Main execution
main() {
    log "🚀 Starting migration verification process..."
    
    validate_environment
    run_tests
    verify_alembic
    verify_docker
    run_coverage
    
    log "🎉 All verifications completed successfully!"
}

# Execute main function
main "$@"
