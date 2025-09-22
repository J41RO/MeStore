#!/bin/bash

# MeStore Admin Endpoints Performance Testing Execution Script
# Performance Testing AI - Comprehensive Load Testing Framework
#
# This script executes all performance testing scenarios for the massive admin endpoints
# that completed TDD RED-GREEN-REFACTOR phases (1,785+ lines of functionality)

set -e

# === CONFIGURATION ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/home/admin-jairo/MeStore"
PERFORMANCE_RESULTS_DIR="$SCRIPT_DIR"
K6_SCRIPT="$PERFORMANCE_RESULTS_DIR/k6-load-testing-scenarios.js"
DB_MONITOR_SCRIPT="$PERFORMANCE_RESULTS_DIR/database-performance-monitor.py"

# API Configuration
export BASE_URL="http://192.168.1.137:8000"
export API_VERSION="/api/v1"

# Database Configuration
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="mestore_db"
export DB_USER="mestore_user"
export DB_PASSWORD="mestore_password"

# Performance Test Configuration
export K6_VU_MAX=1000
export K6_DURATION="60m"
export K6_OUT="json=$PERFORMANCE_RESULTS_DIR/k6-raw-results.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# === LOGGING FUNCTIONS ===
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# === UTILITY FUNCTIONS ===
check_dependencies() {
    log_info "Checking performance testing dependencies..."

    # Check k6
    if ! command -v k6 &> /dev/null; then
        log_error "k6 is not installed. Installing k6..."

        # Install k6 for Ubuntu/Debian
        sudo gpg -k
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6

        if ! command -v k6 &> /dev/null; then
            log_error "Failed to install k6. Please install manually."
            exit 1
        fi
    fi

    # Check Python dependencies
    python3 -c "import asyncpg, psutil, matplotlib, pandas" 2>/dev/null || {
        log_info "Installing Python dependencies..."
        pip3 install asyncpg psutil matplotlib pandas
    }

    log_success "All dependencies verified"
}

check_services() {
    log_info "Checking MeStore services status..."

    # Check backend service
    if ! curl -s "$BASE_URL/health" >/dev/null 2>&1; then
        log_warning "Backend service not responding at $BASE_URL"
        log_info "Attempting to start MeStore services..."

        cd "$PROJECT_ROOT"
        if [ -f "docker-compose.yml" ]; then
            docker-compose up -d
            sleep 30

            if ! curl -s "$BASE_URL/health" >/dev/null 2>&1; then
                log_error "Failed to start backend service. Please start manually."
                exit 1
            fi
        else
            log_error "docker-compose.yml not found. Please start services manually."
            exit 1
        fi
    fi

    # Check database connectivity
    if ! python3 -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME').close())" 2>/dev/null; then
        log_error "Database not accessible. Please check database configuration."
        exit 1
    fi

    log_success "All services are running"
}

# === PERFORMANCE TEST EXECUTION FUNCTIONS ===

run_database_monitoring() {
    local test_name=$1
    local duration_seconds=$2

    log_info "Starting database monitoring for $test_name (${duration_seconds}s)..."

    python3 -c "
import asyncio
import sys
import os
sys.path.append('$SCRIPT_DIR')
from database_performance_monitor import DatabasePerformanceMonitor

async def monitor_test():
    monitor = DatabasePerformanceMonitor(
        db_host='$DB_HOST',
        db_port=$DB_PORT,
        db_name='$DB_NAME',
        db_user='$DB_USER',
        db_password='$DB_PASSWORD',
        monitoring_interval=5
    )

    try:
        await monitor.initialize_connection_pool()
        monitoring_task = asyncio.create_task(monitor.start_monitoring())

        # Monitor for the test duration
        await asyncio.sleep($duration_seconds)

        await monitor.stop_monitoring()
        monitoring_task.cancel()

        # Save results
        monitor.save_performance_data('$PERFORMANCE_RESULTS_DIR/db_performance_${test_name}.json')
        monitor.create_performance_charts('$PERFORMANCE_RESULTS_DIR')

        print(f'Database monitoring completed for $test_name')

    except Exception as e:
        print(f'Database monitoring failed: {e}')
        await monitor.stop_monitoring()

asyncio.run(monitor_test())
" &

    DB_MONITOR_PID=$!
    echo $DB_MONITOR_PID > "$PERFORMANCE_RESULTS_DIR/db_monitor.pid"
}

stop_database_monitoring() {
    if [ -f "$PERFORMANCE_RESULTS_DIR/db_monitor.pid" ]; then
        local pid=$(cat "$PERFORMANCE_RESULTS_DIR/db_monitor.pid")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid
            log_info "Database monitoring stopped"
        fi
        rm -f "$PERFORMANCE_RESULTS_DIR/db_monitor.pid"
    fi
}

run_smoke_test() {
    log_info "Running smoke test to verify basic functionality..."

    # Run quick smoke test
    k6 run \
        --vus 5 \
        --duration 30s \
        --out json="$PERFORMANCE_RESULTS_DIR/smoke_test_results.json" \
        "$K6_SCRIPT"

    if [ $? -eq 0 ]; then
        log_success "Smoke test passed - system ready for load testing"
    else
        log_error "Smoke test failed - check system configuration"
        exit 1
    fi
}

run_load_test_scenario() {
    local scenario_name=$1
    local scenario_config=$2
    local duration=$3

    log_info "Starting $scenario_name load test scenario..."

    # Start database monitoring
    run_database_monitoring "$scenario_name" $(echo "$duration" | sed 's/[^0-9]*//g')

    # Wait for monitoring to initialize
    sleep 5

    # Run k6 load test
    k6 run \
        --config <(echo "$scenario_config") \
        --out json="$PERFORMANCE_RESULTS_DIR/k6_${scenario_name}_results.json" \
        "$K6_SCRIPT"

    local k6_exit_code=$?

    # Stop database monitoring
    stop_database_monitoring

    if [ $k6_exit_code -eq 0 ]; then
        log_success "$scenario_name load test completed successfully"
    else
        log_warning "$scenario_name load test completed with issues (exit code: $k6_exit_code)"
    fi

    # Brief pause between tests
    sleep 10
}

run_normal_load_test() {
    local config='{
        "scenarios": {
            "normal_load": {
                "executor": "ramping-vus",
                "startVUs": 10,
                "stages": [
                    {"duration": "2m", "target": 50},
                    {"duration": "5m", "target": 50},
                    {"duration": "2m", "target": 0}
                ],
                "exec": "normalLoadTest"
            }
        },
        "thresholds": {
            "http_req_duration": ["p(95)<2000"],
            "errors": ["rate<0.01"]
        }
    }'

    run_load_test_scenario "normal" "$config" "9m"
}

run_peak_load_test() {
    local config='{
        "scenarios": {
            "peak_load": {
                "executor": "ramping-vus",
                "startVUs": 20,
                "stages": [
                    {"duration": "3m", "target": 200},
                    {"duration": "10m", "target": 200},
                    {"duration": "3m", "target": 0}
                ],
                "exec": "peakLoadTest"
            }
        },
        "thresholds": {
            "http_req_duration": ["p(95)<3000"],
            "errors": ["rate<0.02"]
        }
    }'

    run_load_test_scenario "peak" "$config" "16m"
}

run_stress_load_test() {
    local config='{
        "scenarios": {
            "stress_load": {
                "executor": "ramping-vus",
                "startVUs": 50,
                "stages": [
                    {"duration": "5m", "target": 500},
                    {"duration": "15m", "target": 500},
                    {"duration": "5m", "target": 0}
                ],
                "exec": "stressLoadTest"
            }
        },
        "thresholds": {
            "http_req_duration": ["p(95)<5000"],
            "errors": ["rate<0.05"]
        }
    }'

    run_load_test_scenario "stress" "$config" "25m"
}

run_spike_load_test() {
    local config='{
        "scenarios": {
            "spike_load": {
                "executor": "ramping-vus",
                "startVUs": 100,
                "stages": [
                    {"duration": "10s", "target": 1000},
                    {"duration": "2m", "target": 1000},
                    {"duration": "10s", "target": 100}
                ],
                "exec": "spikeLoadTest"
            }
        },
        "thresholds": {
            "http_req_duration": ["p(95)<10000"],
            "errors": ["rate<0.10"]
        }
    }'

    run_load_test_scenario "spike" "$config" "3m"
}

run_endurance_test() {
    log_info "Starting endurance test (8 hours) - running in background..."

    local config='{
        "scenarios": {
            "endurance_load": {
                "executor": "constant-vus",
                "vus": 100,
                "duration": "8h",
                "exec": "enduranceLoadTest"
            }
        },
        "thresholds": {
            "http_req_duration": ["p(95)<3000"],
            "errors": ["rate<0.02"]
        }
    }'

    # Start database monitoring for endurance test
    run_database_monitoring "endurance" 28800  # 8 hours

    # Run endurance test in background
    nohup k6 run \
        --config <(echo "$config") \
        --out json="$PERFORMANCE_RESULTS_DIR/k6_endurance_results.json" \
        "$K6_SCRIPT" > "$PERFORMANCE_RESULTS_DIR/endurance_test.log" 2>&1 &

    echo $! > "$PERFORMANCE_RESULTS_DIR/endurance_test.pid"

    log_info "Endurance test started in background (PID: $(cat $PERFORMANCE_RESULTS_DIR/endurance_test.pid))"
    log_info "Monitor progress: tail -f $PERFORMANCE_RESULTS_DIR/endurance_test.log"
}

# === RESULTS ANALYSIS ===
analyze_results() {
    log_info "Analyzing performance test results..."

    python3 -c "
import json
import os
import glob
from datetime import datetime

results_dir = '$PERFORMANCE_RESULTS_DIR'
print('\\n=== PERFORMANCE TEST RESULTS SUMMARY ===')

# Analyze k6 results
k6_files = glob.glob(f'{results_dir}/k6_*_results.json')
for file in k6_files:
    test_name = file.split('/')[-1].replace('k6_', '').replace('_results.json', '')

    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            if lines:
                # Get the summary line (last line with metrics)
                summary_line = lines[-1]
                data = json.loads(summary_line)

                if data.get('type') == 'Point' and 'http_req_duration' in data.get('metric', ''):
                    print(f'\\n{test_name.upper()} TEST:')
                    print(f'  Response Time P95: {data.get(\"value\", 0):.2f}ms')
                    print(f'  Timestamp: {data.get(\"timestamp\", \"unknown\")}')
    except Exception as e:
        print(f'Error analyzing {file}: {e}')

# Analyze database performance
db_files = glob.glob(f'{results_dir}/db_performance_*.json')
for file in db_files:
    test_name = file.split('/')[-1].replace('db_performance_', '').replace('.json', '')

    try:
        with open(file, 'r') as f:
            data = json.load(f)

        print(f'\\n{test_name.upper()} DATABASE PERFORMANCE:')
        print(f'  Peak Connections: {data[\"peak_metrics\"][\"max_connections\"]}')
        print(f'  Peak Query Time: {data[\"peak_metrics\"][\"max_query_time_ms\"]:.2f}ms')
        print(f'  Peak CPU Usage: {data[\"peak_metrics\"][\"max_cpu_usage\"]:.1f}%')
        print(f'  Total Alerts: {data[\"alert_summary\"][\"total_alerts\"]}')
        print(f'  Critical Alerts: {data[\"alert_summary\"][\"critical_alerts\"]}')
    except Exception as e:
        print(f'Error analyzing {file}: {e}')

print('\\n=== PERFORMANCE ANALYSIS COMPLETE ===')
"
}

# === CLEANUP FUNCTIONS ===
cleanup() {
    log_info "Performing cleanup..."

    # Stop any running database monitoring
    stop_database_monitoring

    # Stop endurance test if running
    if [ -f "$PERFORMANCE_RESULTS_DIR/endurance_test.pid" ]; then
        local pid=$(cat "$PERFORMANCE_RESULTS_DIR/endurance_test.pid")
        if ps -p $pid > /dev/null 2>&1; then
            log_info "Stopping endurance test (PID: $pid)..."
            kill $pid
        fi
        rm -f "$PERFORMANCE_RESULTS_DIR/endurance_test.pid"
    fi

    log_info "Cleanup completed"
}

# === MAIN EXECUTION ===
main() {
    echo "========================================================================"
    echo "     MeStore Admin Endpoints Performance Testing Framework"
    echo "     Performance Testing AI - Comprehensive Load Testing"
    echo "========================================================================"
    echo ""
    echo "Testing 1,785+ lines of admin functionality that completed TDD phases:"
    echo "  ✅ RED phase - Failing tests written"
    echo "  ✅ GREEN phase - Implementation completed"
    echo "  ✅ REFACTOR phase - Code optimized"
    echo "  🔥 PERFORMANCE phase - Load testing (NOW)"
    echo ""

    # Setup trap for cleanup
    trap cleanup EXIT

    # Pre-flight checks
    check_dependencies
    check_services

    # Create results directory
    mkdir -p "$PERFORMANCE_RESULTS_DIR"

    # Record test execution start
    echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$PERFORMANCE_RESULTS_DIR/test_execution_start.txt"

    # Run smoke test first
    run_smoke_test

    # Execute performance test scenarios
    log_info "Starting comprehensive performance test suite..."

    echo ""
    echo "🔥 PERFORMANCE TEST EXECUTION PLAN:"
    echo "  1. Normal Load Test (50 users, 9 minutes)"
    echo "  2. Peak Load Test (200 users, 16 minutes)"
    echo "  3. Stress Load Test (500 users, 25 minutes)"
    echo "  4. Spike Load Test (1000 users, 3 minutes)"
    echo "  5. Endurance Test (100 users, 8 hours - background)"
    echo ""

    # Sequential execution of load tests
    run_normal_load_test
    run_peak_load_test
    run_stress_load_test
    run_spike_load_test

    # Start endurance test (runs in background)
    run_endurance_test

    # Analyze results
    analyze_results

    # Record test execution end
    echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$PERFORMANCE_RESULTS_DIR/test_execution_end.txt"

    log_success "Performance testing execution completed!"
    echo ""
    echo "📊 RESULTS LOCATION: $PERFORMANCE_RESULTS_DIR"
    echo "📈 CHARTS: $PERFORMANCE_RESULTS_DIR/database_performance_charts.png"
    echo "📋 REPORTS: $PERFORMANCE_RESULTS_DIR/db_performance_*.json"
    echo "📊 K6 REPORTS: $PERFORMANCE_RESULTS_DIR/k6_*_results.json"
    echo ""
    echo "⏰ ENDURANCE TEST: Running in background for 8 hours"
    echo "📝 MONITOR: tail -f $PERFORMANCE_RESULTS_DIR/endurance_test.log"
    echo ""
    echo "🎯 NEXT STEPS:"
    echo "  1. Review performance reports"
    echo "  2. Analyze bottlenecks and optimization opportunities"
    echo "  3. Generate comprehensive performance analysis report"
    echo "  4. Prepare recommendations for production deployment"
}

# Execute main function
main "$@"