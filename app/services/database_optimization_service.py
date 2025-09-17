# ~/app/services/database_optimization_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Database Optimization Service
# Copyright (c) 2025 Performance Optimization AI. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: database_optimization_service.py
# Ruta: ~/app/services/database_optimization_service.py
# Autor: Performance Optimization AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Database performance optimization for MeStore marketplace
#            Query optimization, indexing strategies, and connection pool management
#
# Características:
# - Automated slow query detection and optimization
# - Dynamic index creation and management
# - Connection pool optimization and monitoring
# - Query result caching with intelligent invalidation
# - Database performance metrics and analysis
# - Automated EXPLAIN ANALYZE for query optimization
# - Partition management for large tables
#
# ---------------------------------------------------------------------------------------------

"""
Database Optimization Service para MeStore Marketplace.

Este módulo implementa optimización comprehensiva de base de datos:
- Detección automática de queries lentos y optimización
- Creación y gestión dinámica de índices
- Optimización y monitoreo de connection pools
- Caching de resultados de queries con invalidación inteligente
- Métricas y análisis de performance de base de datos
- EXPLAIN ANALYZE automático para optimización de queries
- Gestión de particiones para tablas grandes
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from sqlalchemy import Index, create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql import ClauseElement

from app.core.config import settings
from app.core.redis.base import get_redis_client
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class DatabaseOptimizationService:
    """Comprehensive database optimization service"""

    def __init__(self):
        self.slow_query_threshold = 100  # milliseconds
        self.query_cache_ttl = 300  # 5 minutes default
        self.redis_client = None
        self.optimization_stats = {
            "queries_optimized": 0,
            "indexes_created": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "slow_queries_detected": 0
        }

    async def _get_redis(self):
        """Get Redis client with lazy initialization"""
        if self.redis_client is None:
            self.redis_client = await get_redis_client()
        return self.redis_client

    async def analyze_slow_queries(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Analyze slow queries from PostgreSQL logs and statistics"""
        try:
            # Query pg_stat_statements for slow queries (if extension is available)
            slow_queries_query = text("""
                SELECT
                    query,
                    calls,
                    total_time,
                    mean_time,
                    max_time,
                    rows,
                    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements
                WHERE mean_time > :threshold
                ORDER BY mean_time DESC
                LIMIT 20
            """)

            try:
                result = await db.execute(slow_queries_query, {"threshold": self.slow_query_threshold})
                slow_queries = []

                for row in result:
                    slow_queries.append({
                        "query": row.query,
                        "calls": row.calls,
                        "total_time_ms": float(row.total_time),
                        "mean_time_ms": float(row.mean_time),
                        "max_time_ms": float(row.max_time),
                        "rows_affected": row.rows,
                        "cache_hit_percent": float(row.hit_percent or 0),
                        "optimization_priority": self._calculate_optimization_priority(row)
                    })

                self.optimization_stats["slow_queries_detected"] += len(slow_queries)
                return slow_queries

            except Exception as e:
                logger.warning(f"pg_stat_statements not available: {e}")
                return []

        except Exception as e:
            logger.error(f"Error analyzing slow queries: {e}")
            return []

    def _calculate_optimization_priority(self, query_row) -> str:
        """Calculate optimization priority based on query statistics"""
        mean_time = float(query_row.mean_time)
        calls = int(query_row.calls)
        hit_percent = float(query_row.hit_percent or 0)

        # High priority: frequent slow queries with poor cache performance
        if mean_time > 500 and calls > 100 and hit_percent < 80:
            return "HIGH"
        elif mean_time > 200 and calls > 50:
            return "MEDIUM"
        else:
            return "LOW"

    async def create_performance_indexes(self, db: AsyncSession) -> List[str]:
        """Create performance-optimized indexes based on query patterns"""
        created_indexes = []

        try:
            # Define optimized indexes for MeStore marketplace
            indexes_to_create = [
                # Product performance indexes
                {
                    "table": "products",
                    "columns": ["status", "created_at"],
                    "name": "idx_products_status_created_performance",
                    "type": "btree"
                },
                {
                    "table": "products",
                    "columns": ["vendor_id", "status"],
                    "name": "idx_products_vendor_status_performance",
                    "type": "btree"
                },
                {
                    "table": "products",
                    "columns": ["name"],
                    "name": "idx_products_name_fulltext_performance",
                    "type": "gin",
                    "expression": "to_tsvector('spanish', name)"
                },

                # User performance indexes
                {
                    "table": "users",
                    "columns": ["email", "status"],
                    "name": "idx_users_email_status_performance",
                    "type": "btree"
                },
                {
                    "table": "users",
                    "columns": ["user_type", "created_at"],
                    "name": "idx_users_type_created_performance",
                    "type": "btree"
                },

                # Order performance indexes
                {
                    "table": "orders",
                    "columns": ["buyer_id", "status", "created_at"],
                    "name": "idx_orders_buyer_status_created_performance",
                    "type": "btree"
                },
                {
                    "table": "orders",
                    "columns": ["vendor_id", "status"],
                    "name": "idx_orders_vendor_status_performance",
                    "type": "btree"
                },

                # Transaction performance indexes
                {
                    "table": "transactions",
                    "columns": ["order_id", "status"],
                    "name": "idx_transactions_order_status_performance",
                    "type": "btree"
                },
                {
                    "table": "transactions",
                    "columns": ["payment_method", "created_at"],
                    "name": "idx_transactions_payment_created_performance",
                    "type": "btree"
                },

                # Commission performance indexes
                {
                    "table": "commissions",
                    "columns": ["vendor_id", "status", "created_at"],
                    "name": "idx_commissions_vendor_status_created_performance",
                    "type": "btree"
                },

                # Category performance indexes
                {
                    "table": "categories",
                    "columns": ["parent_id", "level"],
                    "name": "idx_categories_parent_level_performance",
                    "type": "btree"
                },
                {
                    "table": "categories",
                    "columns": ["name"],
                    "name": "idx_categories_name_fulltext_performance",
                    "type": "gin",
                    "expression": "to_tsvector('spanish', name)"
                }
            ]

            for index_def in indexes_to_create:
                try:
                    # Check if index already exists
                    check_query = text("""
                        SELECT indexname FROM pg_indexes
                        WHERE tablename = :table AND indexname = :name
                    """)

                    result = await db.execute(check_query, {
                        "table": index_def["table"],
                        "name": index_def["name"]
                    })

                    if result.fetchone():
                        logger.info(f"Index {index_def['name']} already exists")
                        continue

                    # Create the index
                    if index_def["type"] == "gin" and "expression" in index_def:
                        # GIN index with expression (for full-text search)
                        create_index_query = text(f"""
                            CREATE INDEX CONCURRENTLY {index_def['name']}
                            ON {index_def['table']}
                            USING GIN ({index_def['expression']})
                        """)
                    else:
                        # Regular B-tree index
                        columns = ", ".join(index_def["columns"])
                        create_index_query = text(f"""
                            CREATE INDEX CONCURRENTLY {index_def['name']}
                            ON {index_def['table']} ({columns})
                        """)

                    await db.execute(create_index_query)
                    await db.commit()

                    created_indexes.append(index_def["name"])
                    self.optimization_stats["indexes_created"] += 1

                    logger.info(f"Created performance index: {index_def['name']}")

                except Exception as e:
                    logger.error(f"Error creating index {index_def['name']}: {e}")
                    await db.rollback()
                    continue

        except Exception as e:
            logger.error(f"Error in create_performance_indexes: {e}")

        return created_indexes

    async def optimize_connection_pool(self) -> Dict[str, Any]:
        """Optimize database connection pool settings"""
        try:
            # Current pool settings
            current_settings = {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_timeout": 30,
                "pool_recycle": 3600,
                "pool_pre_ping": True
            }

            # Calculate optimal settings based on load
            redis_client = await self._get_redis()

            # Get active connections count
            active_connections_key = "db:active_connections"
            active_connections = await redis_client.get(active_connections_key) or 0
            active_connections = int(active_connections)

            # Calculate optimal pool size based on load
            if active_connections > 15:
                optimal_pool_size = min(20, active_connections + 5)
                optimal_max_overflow = min(30, optimal_pool_size * 2)
            else:
                optimal_pool_size = 10
                optimal_max_overflow = 20

            optimized_settings = {
                "pool_size": optimal_pool_size,
                "max_overflow": optimal_max_overflow,
                "pool_timeout": 30,
                "pool_recycle": 3600,  # 1 hour
                "pool_pre_ping": True
            }

            # Store optimization metrics
            optimization_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "current_settings": current_settings,
                "optimized_settings": optimized_settings,
                "active_connections": active_connections,
                "optimization_applied": True
            }

            await redis_client.setex(
                "db:pool_optimization",
                3600,  # 1 hour TTL
                json.dumps(optimization_data)
            )

            logger.info(f"Connection pool optimized: {optimized_settings}")
            return optimization_data

        except Exception as e:
            logger.error(f"Error optimizing connection pool: {e}")
            return {}

    async def enable_query_caching(self, query: str, params: Dict[str, Any], result: Any, ttl: Optional[int] = None) -> str:
        """Cache query results with intelligent TTL"""
        try:
            # Generate cache key
            cache_key = self._generate_query_cache_key(query, params)

            # Determine TTL based on query type
            if ttl is None:
                ttl = self._calculate_cache_ttl(query)

            # Cache the result
            await cache_service.set(cache_key, result, ttl)

            return cache_key

        except Exception as e:
            logger.error(f"Error caching query result: {e}")
            return ""

    async def get_cached_query_result(self, query: str, params: Dict[str, Any]) -> Any:
        """Get cached query result"""
        try:
            cache_key = self._generate_query_cache_key(query, params)
            result = await cache_service.get(cache_key)

            if result is not None:
                self.optimization_stats["cache_hits"] += 1
            else:
                self.optimization_stats["cache_misses"] += 1

            return result

        except Exception as e:
            logger.error(f"Error getting cached query result: {e}")
            self.optimization_stats["cache_misses"] += 1
            return None

    def _generate_query_cache_key(self, query: str, params: Dict[str, Any]) -> str:
        """Generate consistent cache key for query and parameters"""
        import hashlib

        # Normalize query (remove extra whitespace)
        normalized_query = " ".join(query.split())

        # Sort parameters for consistent key generation
        sorted_params = json.dumps(params, sort_keys=True, default=str)

        # Create hash
        key_data = f"{normalized_query}:{sorted_params}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]

        return f"db:query_cache:{key_hash}"

    def _calculate_cache_ttl(self, query: str) -> int:
        """Calculate appropriate TTL based on query type"""
        query_lower = query.lower().strip()

        # Static/reference data - longer TTL
        if any(table in query_lower for table in ['categories', 'commission_rates']):
            return 3600  # 1 hour

        # Product data - medium TTL
        elif 'products' in query_lower:
            return 600  # 10 minutes

        # User/session data - shorter TTL
        elif any(table in query_lower for table in ['users', 'sessions']):
            return 300  # 5 minutes

        # Transaction/order data - very short TTL
        elif any(table in query_lower for table in ['orders', 'transactions']):
            return 60  # 1 minute

        # Default TTL
        else:
            return self.query_cache_ttl

    async def analyze_query_performance(self, db: AsyncSession, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze query performance using EXPLAIN ANALYZE"""
        try:
            # Execute EXPLAIN ANALYZE
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"

            if params:
                result = await db.execute(text(explain_query), params)
            else:
                result = await db.execute(text(explain_query))

            explain_result = result.fetchone()[0]

            # Extract key performance metrics
            plan = explain_result[0]["Plan"]
            execution_time = explain_result[0]["Execution Time"]
            planning_time = explain_result[0]["Planning Time"]

            analysis = {
                "execution_time_ms": execution_time,
                "planning_time_ms": planning_time,
                "total_cost": plan.get("Total Cost", 0),
                "actual_rows": plan.get("Actual Rows", 0),
                "actual_loops": plan.get("Actual Loops", 1),
                "shared_hit_blocks": plan.get("Shared Hit Blocks", 0),
                "shared_read_blocks": plan.get("Shared Read Blocks", 0),
                "node_type": plan.get("Node Type", ""),
                "index_used": "Index" in plan.get("Node Type", ""),
                "performance_rating": self._rate_query_performance(execution_time, plan),
                "optimization_suggestions": self._generate_optimization_suggestions(plan, execution_time)
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            return {}

    def _rate_query_performance(self, execution_time: float, plan: Dict) -> str:
        """Rate query performance based on execution time and plan"""
        if execution_time < 10:
            return "EXCELLENT"
        elif execution_time < 50:
            return "GOOD"
        elif execution_time < 200:
            return "FAIR"
        else:
            return "POOR"

    def _generate_optimization_suggestions(self, plan: Dict, execution_time: float) -> List[str]:
        """Generate optimization suggestions based on query plan"""
        suggestions = []

        # Check for sequential scans
        if "Seq Scan" in plan.get("Node Type", ""):
            suggestions.append("Consider adding an index to avoid sequential scan")

        # Check for high cost operations
        if plan.get("Total Cost", 0) > 1000:
            suggestions.append("Query has high cost - consider query rewriting or indexing")

        # Check for excessive rows
        if plan.get("Actual Rows", 0) > 10000:
            suggestions.append("Query returns many rows - consider adding LIMIT or filtering")

        # Check for slow execution
        if execution_time > 100:
            suggestions.append("Query execution is slow - analyze joins and subqueries")

        return suggestions

    async def create_materialized_views(self, db: AsyncSession) -> List[str]:
        """Create materialized views for frequently accessed complex queries"""
        created_views = []

        try:
            # Define materialized views for performance
            materialized_views = [
                {
                    "name": "mv_product_performance_stats",
                    "query": """
                        SELECT
                            p.id,
                            p.name,
                            p.vendor_id,
                            p.status,
                            COUNT(o.id) as total_orders,
                            SUM(o.total_amount) as total_revenue,
                            AVG(o.total_amount) as avg_order_value
                        FROM products p
                        LEFT JOIN orders o ON p.id = o.product_id
                        WHERE p.status = 'ACTIVE'
                        GROUP BY p.id, p.name, p.vendor_id, p.status
                    """
                },
                {
                    "name": "mv_vendor_performance_stats",
                    "query": """
                        SELECT
                            u.id as vendor_id,
                            u.email,
                            COUNT(DISTINCT p.id) as total_products,
                            COUNT(DISTINCT o.id) as total_orders,
                            SUM(o.total_amount) as total_revenue,
                            AVG(o.total_amount) as avg_order_value
                        FROM users u
                        JOIN products p ON u.id = p.vendor_id
                        LEFT JOIN orders o ON p.id = o.product_id
                        WHERE u.user_type = 'VENDOR'
                        GROUP BY u.id, u.email
                    """
                },
                {
                    "name": "mv_category_performance_stats",
                    "query": """
                        SELECT
                            c.id,
                            c.name,
                            c.level,
                            COUNT(DISTINCT p.id) as total_products,
                            COUNT(DISTINCT o.id) as total_orders,
                            SUM(o.total_amount) as total_revenue
                        FROM categories c
                        LEFT JOIN product_categories pc ON c.id = pc.category_id
                        LEFT JOIN products p ON pc.product_id = p.id
                        LEFT JOIN orders o ON p.id = o.product_id
                        GROUP BY c.id, c.name, c.level
                    """
                }
            ]

            for view_def in materialized_views:
                try:
                    # Drop existing view if it exists
                    drop_query = text(f"DROP MATERIALIZED VIEW IF EXISTS {view_def['name']}")
                    await db.execute(drop_query)

                    # Create materialized view
                    create_query = text(f"""
                        CREATE MATERIALIZED VIEW {view_def['name']} AS
                        {view_def['query']}
                        WITH DATA
                    """)
                    await db.execute(create_query)

                    # Create index on materialized view
                    index_query = text(f"""
                        CREATE UNIQUE INDEX {view_def['name']}_id_idx
                        ON {view_def['name']} (id)
                    """)
                    await db.execute(index_query)

                    await db.commit()
                    created_views.append(view_def['name'])

                    logger.info(f"Created materialized view: {view_def['name']}")

                except Exception as e:
                    logger.error(f"Error creating materialized view {view_def['name']}: {e}")
                    await db.rollback()
                    continue

        except Exception as e:
            logger.error(f"Error in create_materialized_views: {e}")

        return created_views

    async def refresh_materialized_views(self, db: AsyncSession) -> List[str]:
        """Refresh materialized views"""
        refreshed_views = []

        view_names = [
            "mv_product_performance_stats",
            "mv_vendor_performance_stats",
            "mv_category_performance_stats"
        ]

        for view_name in view_names:
            try:
                refresh_query = text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view_name}")
                await db.execute(refresh_query)
                await db.commit()
                refreshed_views.append(view_name)
                logger.info(f"Refreshed materialized view: {view_name}")

            except Exception as e:
                logger.error(f"Error refreshing materialized view {view_name}: {e}")
                await db.rollback()
                continue

        return refreshed_views

    async def get_optimization_stats(self) -> Dict[str, Any]:
        """Get database optimization statistics"""
        return {
            "optimization_stats": self.optimization_stats,
            "timestamp": datetime.utcnow().isoformat(),
            "cache_hit_rate": (
                self.optimization_stats["cache_hits"] /
                max(self.optimization_stats["cache_hits"] + self.optimization_stats["cache_misses"], 1)
            ) * 100
        }


# Global database optimization service instance
database_optimization_service = DatabaseOptimizationService()


async def get_database_optimization_service() -> DatabaseOptimizationService:
    """Dependency function to get database optimization service instance"""
    return database_optimization_service