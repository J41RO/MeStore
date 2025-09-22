#!/usr/bin/env python3
"""
Database Performance Monitor for MeStore Admin Endpoints Load Testing
Performance Testing AI - Advanced Database Monitoring Framework

This module provides comprehensive database performance monitoring during load tests,
including connection pool analysis, query performance tracking, and resource utilization.
"""

import asyncio
import psutil
import time
import json
import logging
import asyncpg
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DatabaseMetrics:
    """Database performance metrics snapshot."""
    timestamp: datetime
    active_connections: int
    idle_connections: int
    total_connections: int
    connection_pool_usage: float
    avg_query_time_ms: float
    slow_queries_count: int
    deadlocks_count: int
    cpu_usage_percent: float
    memory_usage_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    cache_hit_ratio: float
    transaction_rate: float
    lock_waits: int

@dataclass
class QueryPerformanceMetrics:
    """Individual query performance metrics."""
    query_hash: str
    query_text: str
    execution_count: int
    avg_execution_time_ms: float
    max_execution_time_ms: float
    total_execution_time_ms: float
    rows_affected: int
    cache_hits: int
    cache_misses: int

class DatabasePerformanceMonitor:
    """
    Comprehensive database performance monitoring system for load testing.

    Monitors PostgreSQL performance during admin endpoint load tests with
    real-time metrics collection and analysis.
    """

    def __init__(self,
                 db_host: str = "localhost",
                 db_port: int = 5432,
                 db_name: str = "mestore_db",
                 db_user: str = "mestore_user",
                 db_password: str = "mestore_password",
                 monitoring_interval: int = 5):
        """
        Initialize the database performance monitor.

        Args:
            db_host: Database server hostname
            db_port: Database server port
            db_name: Database name
            db_user: Database username
            db_password: Database password
            monitoring_interval: Monitoring interval in seconds
        """
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.monitoring_interval = monitoring_interval

        self.metrics_history: List[DatabaseMetrics] = []
        self.query_metrics: Dict[str, QueryPerformanceMetrics] = {}
        self.monitoring_active = False
        self.db_pool: Optional[asyncpg.Pool] = None

        # Performance baselines
        self.baseline_metrics: Optional[DatabaseMetrics] = None
        self.performance_alerts: List[Dict[str, Any]] = []

    async def initialize_connection_pool(self) -> None:
        """Initialize database connection pool for monitoring."""
        try:
            self.db_pool = await asyncpg.create_pool(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                min_size=1,
                max_size=5,
                command_timeout=30
            )
            logger.info("Database connection pool initialized for monitoring")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise

    async def start_monitoring(self) -> None:
        """Start continuous database performance monitoring."""
        if not self.db_pool:
            await self.initialize_connection_pool()

        self.monitoring_active = True
        logger.info(f"Starting database performance monitoring (interval: {self.monitoring_interval}s)")

        # Collect baseline metrics
        await self._collect_baseline_metrics()

        # Start monitoring loop
        while self.monitoring_active:
            try:
                metrics = await self._collect_performance_metrics()
                self.metrics_history.append(metrics)

                # Check for performance alerts
                await self._check_performance_alerts(metrics)

                # Log current status
                logger.info(f"DB Metrics - Connections: {metrics.total_connections}, "
                          f"Avg Query Time: {metrics.avg_query_time_ms:.2f}ms, "
                          f"CPU: {metrics.cpu_usage_percent:.1f}%, "
                          f"Memory: {metrics.memory_usage_mb:.1f}MB")

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error during monitoring cycle: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def stop_monitoring(self) -> None:
        """Stop database performance monitoring."""
        self.monitoring_active = False
        if self.db_pool:
            await self.db_pool.close()
        logger.info("Database performance monitoring stopped")

    async def _collect_baseline_metrics(self) -> None:
        """Collect baseline performance metrics before load testing."""
        logger.info("Collecting baseline database performance metrics...")
        baseline = await self._collect_performance_metrics()
        self.baseline_metrics = baseline
        logger.info(f"Baseline established - Connections: {baseline.total_connections}, "
                   f"Query Time: {baseline.avg_query_time_ms:.2f}ms")

    async def _collect_performance_metrics(self) -> DatabaseMetrics:
        """Collect comprehensive database performance metrics."""
        timestamp = datetime.utcnow()

        # Collect PostgreSQL-specific metrics
        async with self.db_pool.acquire() as conn:
            # Connection metrics
            connection_stats = await conn.fetchrow("""
                SELECT
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle') as idle_connections,
                    (SELECT count(*) FROM pg_stat_activity) as total_connections
            """)

            # Query performance metrics
            query_stats = await conn.fetchrow("""
                SELECT
                    COALESCE(AVG(mean_exec_time), 0) as avg_query_time,
                    COALESCE(COUNT(*) FILTER (WHERE mean_exec_time > 1000), 0) as slow_queries,
                    COALESCE(SUM(calls), 0) as total_queries
                FROM pg_stat_statements
                WHERE last_exec > NOW() - INTERVAL '1 minute'
            """)

            # Database activity metrics
            db_stats = await conn.fetchrow("""
                SELECT
                    COALESCE(xact_commit + xact_rollback, 0) as transaction_rate,
                    COALESCE(deadlocks, 0) as deadlocks,
                    COALESCE(blks_hit::float / NULLIF(blks_hit + blks_read, 0) * 100, 0) as cache_hit_ratio
                FROM pg_stat_database
                WHERE datname = $1
            """, self.db_name)

            # Lock information
            lock_stats = await conn.fetchrow("""
                SELECT COUNT(*) as lock_waits
                FROM pg_stat_activity
                WHERE wait_event_type = 'Lock' AND state = 'active'
            """)

        # System resource metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()

        # Calculate connection pool usage
        pool_usage = (connection_stats['total_connections'] / 100.0) * 100  # Assuming max 100 connections

        return DatabaseMetrics(
            timestamp=timestamp,
            active_connections=connection_stats['active_connections'],
            idle_connections=connection_stats['idle_connections'],
            total_connections=connection_stats['total_connections'],
            connection_pool_usage=min(pool_usage, 100.0),
            avg_query_time_ms=float(query_stats['avg_query_time'] or 0),
            slow_queries_count=query_stats['slow_queries'],
            deadlocks_count=db_stats['deadlocks'],
            cpu_usage_percent=cpu_percent,
            memory_usage_mb=memory.used / 1024 / 1024,
            disk_io_read_mb=disk_io.read_bytes / 1024 / 1024 if disk_io else 0,
            disk_io_write_mb=disk_io.write_bytes / 1024 / 1024 if disk_io else 0,
            cache_hit_ratio=float(db_stats['cache_hit_ratio'] or 0),
            transaction_rate=float(db_stats['transaction_rate'] or 0),
            lock_waits=lock_stats['lock_waits']
        )

    async def _check_performance_alerts(self, current_metrics: DatabaseMetrics) -> None:
        """Check for performance degradation and generate alerts."""
        alerts = []

        if self.baseline_metrics:
            # Connection pool usage alert
            if current_metrics.connection_pool_usage > 80:
                alerts.append({
                    'type': 'HIGH_CONNECTION_USAGE',
                    'severity': 'WARNING',
                    'message': f'Connection pool usage at {current_metrics.connection_pool_usage:.1f}%',
                    'timestamp': current_metrics.timestamp,
                    'value': current_metrics.connection_pool_usage
                })

            # Query performance degradation
            baseline_query_time = self.baseline_metrics.avg_query_time_ms
            if (current_metrics.avg_query_time_ms > baseline_query_time * 2 and
                current_metrics.avg_query_time_ms > 100):
                alerts.append({
                    'type': 'QUERY_PERFORMANCE_DEGRADATION',
                    'severity': 'CRITICAL',
                    'message': f'Average query time increased to {current_metrics.avg_query_time_ms:.2f}ms '
                              f'(baseline: {baseline_query_time:.2f}ms)',
                    'timestamp': current_metrics.timestamp,
                    'value': current_metrics.avg_query_time_ms
                })

            # High CPU usage
            if current_metrics.cpu_usage_percent > 90:
                alerts.append({
                    'type': 'HIGH_CPU_USAGE',
                    'severity': 'CRITICAL',
                    'message': f'CPU usage at {current_metrics.cpu_usage_percent:.1f}%',
                    'timestamp': current_metrics.timestamp,
                    'value': current_metrics.cpu_usage_percent
                })

            # Low cache hit ratio
            if current_metrics.cache_hit_ratio < 90:
                alerts.append({
                    'type': 'LOW_CACHE_HIT_RATIO',
                    'severity': 'WARNING',
                    'message': f'Cache hit ratio at {current_metrics.cache_hit_ratio:.1f}%',
                    'timestamp': current_metrics.timestamp,
                    'value': current_metrics.cache_hit_ratio
                })

            # Deadlock detection
            if current_metrics.deadlocks_count > 0:
                alerts.append({
                    'type': 'DEADLOCKS_DETECTED',
                    'severity': 'WARNING',
                    'message': f'{current_metrics.deadlocks_count} deadlocks detected',
                    'timestamp': current_metrics.timestamp,
                    'value': current_metrics.deadlocks_count
                })

        # Log alerts
        for alert in alerts:
            logger.warning(f"PERFORMANCE ALERT [{alert['severity']}]: {alert['message']}")
            self.performance_alerts.append(alert)

    async def get_slow_queries(self, limit: int = 10) -> List[QueryPerformanceMetrics]:
        """Get the slowest queries during the monitoring period."""
        if not self.db_pool:
            return []

        async with self.db_pool.acquire() as conn:
            slow_queries = await conn.fetch("""
                SELECT
                    query,
                    calls as execution_count,
                    mean_exec_time as avg_execution_time_ms,
                    max_exec_time as max_execution_time_ms,
                    total_exec_time as total_execution_time_ms,
                    rows as rows_affected,
                    shared_blks_hit as cache_hits,
                    shared_blks_read as cache_misses
                FROM pg_stat_statements
                ORDER BY mean_exec_time DESC
                LIMIT $1
            """, limit)

            return [
                QueryPerformanceMetrics(
                    query_hash=str(hash(query['query'])),
                    query_text=query['query'][:200] + "..." if len(query['query']) > 200 else query['query'],
                    execution_count=query['execution_count'],
                    avg_execution_time_ms=float(query['avg_execution_time_ms']),
                    max_execution_time_ms=float(query['max_execution_time_ms']),
                    total_execution_time_ms=float(query['total_execution_time_ms']),
                    rows_affected=query['rows_affected'],
                    cache_hits=query['cache_hits'],
                    cache_misses=query['cache_misses']
                )
                for query in slow_queries
            ]

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive database performance report."""
        if not self.metrics_history:
            return {'error': 'No metrics collected'}

        # Calculate performance statistics
        df = pd.DataFrame([
            {
                'timestamp': m.timestamp,
                'total_connections': m.total_connections,
                'avg_query_time_ms': m.avg_query_time_ms,
                'cpu_usage_percent': m.cpu_usage_percent,
                'memory_usage_mb': m.memory_usage_mb,
                'cache_hit_ratio': m.cache_hit_ratio,
                'transaction_rate': m.transaction_rate
            }
            for m in self.metrics_history
        ])

        performance_summary = {
            'monitoring_duration_minutes': len(self.metrics_history) * (self.monitoring_interval / 60),
            'total_data_points': len(self.metrics_history),
            'baseline_metrics': {
                'total_connections': self.baseline_metrics.total_connections if self.baseline_metrics else 0,
                'avg_query_time_ms': self.baseline_metrics.avg_query_time_ms if self.baseline_metrics else 0,
                'cpu_usage_percent': self.baseline_metrics.cpu_usage_percent if self.baseline_metrics else 0
            },
            'peak_metrics': {
                'max_connections': df['total_connections'].max(),
                'max_query_time_ms': df['avg_query_time_ms'].max(),
                'max_cpu_usage': df['cpu_usage_percent'].max(),
                'max_memory_usage_mb': df['memory_usage_mb'].max()
            },
            'average_metrics': {
                'avg_connections': df['total_connections'].mean(),
                'avg_query_time_ms': df['avg_query_time_ms'].mean(),
                'avg_cpu_usage': df['cpu_usage_percent'].mean(),
                'avg_cache_hit_ratio': df['cache_hit_ratio'].mean()
            },
            'performance_alerts': self.performance_alerts,
            'alert_summary': {
                'total_alerts': len(self.performance_alerts),
                'critical_alerts': len([a for a in self.performance_alerts if a['severity'] == 'CRITICAL']),
                'warning_alerts': len([a for a in self.performance_alerts if a['severity'] == 'WARNING'])
            }
        }

        return performance_summary

    def save_performance_data(self, output_file: str) -> None:
        """Save performance data to JSON file."""
        performance_report = self.generate_performance_report()

        # Add raw metrics data
        performance_report['raw_metrics'] = [
            {
                'timestamp': m.timestamp.isoformat(),
                'active_connections': m.active_connections,
                'idle_connections': m.idle_connections,
                'total_connections': m.total_connections,
                'connection_pool_usage': m.connection_pool_usage,
                'avg_query_time_ms': m.avg_query_time_ms,
                'slow_queries_count': m.slow_queries_count,
                'deadlocks_count': m.deadlocks_count,
                'cpu_usage_percent': m.cpu_usage_percent,
                'memory_usage_mb': m.memory_usage_mb,
                'disk_io_read_mb': m.disk_io_read_mb,
                'disk_io_write_mb': m.disk_io_write_mb,
                'cache_hit_ratio': m.cache_hit_ratio,
                'transaction_rate': m.transaction_rate,
                'lock_waits': m.lock_waits
            }
            for m in self.metrics_history
        ]

        with open(output_file, 'w') as f:
            json.dump(performance_report, f, indent=2, default=str)

        logger.info(f"Performance data saved to {output_file}")

    def create_performance_charts(self, output_dir: str) -> None:
        """Create performance visualization charts."""
        if not self.metrics_history:
            logger.warning("No metrics data available for charts")
            return

        # Prepare data
        timestamps = [m.timestamp for m in self.metrics_history]
        connections = [m.total_connections for m in self.metrics_history]
        query_times = [m.avg_query_time_ms for m in self.metrics_history]
        cpu_usage = [m.cpu_usage_percent for m in self.metrics_history]
        cache_hit_ratios = [m.cache_hit_ratio for m in self.metrics_history]

        # Create multi-panel chart
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Database Performance During Load Testing', fontsize=16)

        # Connections chart
        ax1.plot(timestamps, connections, 'b-', linewidth=2)
        ax1.set_title('Database Connections')
        ax1.set_ylabel('Connection Count')
        ax1.grid(True, alpha=0.3)

        # Query performance chart
        ax2.plot(timestamps, query_times, 'r-', linewidth=2)
        ax2.set_title('Average Query Response Time')
        ax2.set_ylabel('Response Time (ms)')
        ax2.grid(True, alpha=0.3)

        # CPU usage chart
        ax3.plot(timestamps, cpu_usage, 'g-', linewidth=2)
        ax3.set_title('CPU Usage')
        ax3.set_ylabel('CPU Usage (%)')
        ax3.set_xlabel('Time')
        ax3.grid(True, alpha=0.3)

        # Cache hit ratio chart
        ax4.plot(timestamps, cache_hit_ratios, 'm-', linewidth=2)
        ax4.set_title('Cache Hit Ratio')
        ax4.set_ylabel('Hit Ratio (%)')
        ax4.set_xlabel('Time')
        ax4.grid(True, alpha=0.3)

        # Format x-axis for all subplots
        for ax in [ax1, ax2, ax3, ax4]:
            ax.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        chart_file = f"{output_dir}/database_performance_charts.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Performance charts saved to {chart_file}")

# === USAGE EXAMPLE ===
async def main():
    """Example usage of the database performance monitor."""
    monitor = DatabasePerformanceMonitor(
        db_host="localhost",
        db_port=5432,
        db_name="mestore_db",
        monitoring_interval=5
    )

    try:
        # Start monitoring
        await monitor.initialize_connection_pool()

        # Run monitoring for a specific duration (e.g., during load test)
        monitoring_task = asyncio.create_task(monitor.start_monitoring())

        # Simulate load test duration
        logger.info("Simulating load test for 60 seconds...")
        await asyncio.sleep(60)

        # Stop monitoring
        await monitor.stop_monitoring()
        await monitoring_task

        # Generate reports
        performance_report = monitor.generate_performance_report()
        monitor.save_performance_data('/tmp/db_performance_report.json')
        monitor.create_performance_charts('/tmp')

        # Get slow queries
        slow_queries = await monitor.get_slow_queries(limit=5)

        print("\n=== Database Performance Summary ===")
        print(f"Monitoring Duration: {performance_report['monitoring_duration_minutes']:.1f} minutes")
        print(f"Peak Connections: {performance_report['peak_metrics']['max_connections']}")
        print(f"Peak Query Time: {performance_report['peak_metrics']['max_query_time_ms']:.2f}ms")
        print(f"Peak CPU Usage: {performance_report['peak_metrics']['max_cpu_usage']:.1f}%")
        print(f"Total Alerts: {performance_report['alert_summary']['total_alerts']}")

        print(f"\n=== Top {len(slow_queries)} Slow Queries ===")
        for i, query in enumerate(slow_queries, 1):
            print(f"{i}. {query.query_text}")
            print(f"   Avg Time: {query.avg_execution_time_ms:.2f}ms, Executions: {query.execution_count}")

    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        await monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())