#!/bin/bash
# Railway Startup Script
# ======================
# This script runs database migrations and then starts the FastAPI server.
# Used by Railway for automatic deployment.

set -e  # Exit on any error

echo "=================================================="
echo "🚀 RAILWAY STARTUP SCRIPT"
echo "=================================================="
echo ""

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
error_exit() {
    log "❌ ERROR: $1"
    exit 1
}

# Step 1: Verify environment
log "📋 Checking environment variables..."
if [ -z "$DATABASE_URL" ]; then
    error_exit "DATABASE_URL not set"
fi
if [ -z "$PORT" ]; then
    log "⚠️  PORT not set, using default 8000"
    PORT=8000
fi
log "✅ Environment validated"
echo ""

# Step 2: Run database migrations
log "🔄 Running Alembic migrations..."
if alembic upgrade head; then
    log "✅ Migrations completed successfully"
else
    error_exit "Alembic migrations failed"
fi
echo ""

# Step 3: Create admin user if needed
log "👤 Ensuring admin user exists..."
if python scripts/create_admin_on_startup.py; then
    log "✅ Admin user check completed"
else
    log "⚠️  Admin user creation failed (non-critical)"
fi
echo ""

# Step 4: Start the application
log "🚀 Starting FastAPI application..."
log "   Host: 0.0.0.0"
log "   Port: $PORT"
echo ""

exec uvicorn app.main_production:app --host 0.0.0.0 --port "$PORT"
