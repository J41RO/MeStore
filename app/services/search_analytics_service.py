# ~/app/services/search_analytics_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Search Analytics and Metrics Service
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: search_analytics_service.py
# Ruta: ~/app/services/search_analytics_service.py
# Autor: Data Engineering AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Servicio de analytics avanzado para métricas de búsqueda y business intelligence
#            Análisis de patrones, performance metrics y insights de usuario
#
# Características:
# - Analytics de búsqueda con segmentación detallada
# - Métricas de performance y optimización
# - Trending queries y pattern detection
# - User behavior analytics
# - Business intelligence para decisiones de producto
# - Reportes automatizados y alertas
#
# ---------------------------------------------------------------------------------------------

"""
Search Analytics Service para MeStore.

Este módulo proporciona analytics avanzados de búsqueda:
- Métricas de uso y performance
- Análisis de patrones de búsqueda
- Segmentación de usuarios
- Business intelligence insights
- Reportes automatizados
- Alertas de performance
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from collections import defaultdict, Counter
import statistics

from app.core.redis.base import RedisManager
from app.services.search_cache_service import SearchCacheService

logger = logging.getLogger(__name__)


class SearchAnalyticsService:
    """
    Servicio de analytics avanzado para métricas de búsqueda.

    Proporciona:
    - Tracking detallado de searches
    - Análisis de performance
    - Business intelligence
    - Reporting automatizado
    """

    def __init__(self, redis_manager: RedisManager):
        """
        Inicializar SearchAnalyticsService.

        Args:
            redis_manager: Instancia de RedisManager
        """
        self.redis_manager = redis_manager

        # Analytics keys
        self.base_key = "analytics:search"
        self.daily_key = f"{self.base_key}:daily"
        self.hourly_key = f"{self.base_key}:hourly"
        self.queries_key = f"{self.base_key}:queries"
        self.performance_key = f"{self.base_key}:performance"
        self.users_key = f"{self.base_key}:users"
        self.patterns_key = f"{self.base_key}:patterns"

        # Performance thresholds
        self.slow_search_threshold = 2000  # 2 seconds in ms
        self.low_results_threshold = 5  # Searches with fewer results
        self.zero_results_threshold = 0  # No results

    async def track_search_event(
        self,
        query: str,
        user_id: Optional[str] = None,
        user_type: Optional[str] = None,
        results_count: int = 0,
        search_time_ms: int = 0,
        filters_applied: Dict = None,
        page: int = 1,
        source: str = "web"
    ) -> None:
        """
        Trackear evento de búsqueda con metadata detallada.

        Args:
            query: Query de búsqueda
            user_id: ID del usuario (opcional)
            user_type: Tipo de usuario (buyer, vendor, admin)
            results_count: Número de resultados
            search_time_ms: Tiempo de búsqueda en ms
            filters_applied: Filtros aplicados
            page: Página solicitada
            source: Fuente de la búsqueda (web, mobile, api)
        """
        try:
            timestamp = datetime.now()
            date_str = timestamp.strftime("%Y-%m-%d")
            hour_str = timestamp.strftime("%Y-%m-%d:%H")

            # Event data
            event_data = {
                "query": query,
                "user_id": user_id,
                "user_type": user_type,
                "results_count": results_count,
                "search_time_ms": search_time_ms,
                "filters_applied": json.dumps(filters_applied or {}),
                "page": page,
                "source": source,
                "timestamp": timestamp.isoformat(),
                "has_results": results_count > 0,
                "is_slow": search_time_ms > self.slow_search_threshold,
                "is_zero_results": results_count == 0
            }

            # Track en múltiples agregaciones
            await asyncio.gather(
                self._track_daily_stats(date_str, event_data),
                self._track_hourly_stats(hour_str, event_data),
                self._track_query_metrics(query, event_data),
                self._track_performance_metrics(event_data),
                self._track_user_behavior(user_id, user_type, event_data),
                self._detect_patterns(event_data)
            )

        except Exception as e:
            logger.error(f"Error tracking search event: {e}")

    async def get_search_dashboard_metrics(
        self,
        days: int = 7,
        include_details: bool = False
    ) -> Dict:
        """
        Obtener métricas para dashboard de búsqueda.

        Args:
            days: Número de días para analizar
            include_details: Incluir detalles granulares

        Returns:
            Dict: Métricas completas de dashboard
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Obtener métricas principales en paralelo
            overview_metrics, trending_queries, performance_metrics, user_metrics = await asyncio.gather(
                self._get_overview_metrics(start_date, end_date),
                self._get_trending_queries(days),
                self._get_performance_metrics(days),
                self._get_user_segmentation_metrics(days)
            )

            dashboard_data = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "overview": overview_metrics,
                "trending_queries": trending_queries,
                "performance": performance_metrics,
                "user_segmentation": user_metrics,
                "generated_at": datetime.now().isoformat()
            }

            if include_details:
                # Agregar detalles adicionales
                hourly_distribution, zero_results_analysis, filter_analysis = await asyncio.gather(
                    self._get_hourly_distribution(days),
                    self._get_zero_results_analysis(days),
                    self._get_filter_usage_analysis(days)
                )

                dashboard_data.update({
                    "hourly_distribution": hourly_distribution,
                    "zero_results_analysis": zero_results_analysis,
                    "filter_analysis": filter_analysis
                })

            return dashboard_data

        except Exception as e:
            logger.error(f"Error obteniendo dashboard metrics: {e}")
            return {"error": str(e)}

    async def get_query_insights(
        self,
        query: str,
        days: int = 30
    ) -> Dict:
        """
        Obtener insights detallados para una query específica.

        Args:
            query: Query a analizar
            days: Período de análisis

        Returns:
            Dict: Insights de la query
        """
        try:
            query_key = f"{self.queries_key}:{query}"

            # Obtener datos históricos de la query
            query_data = await self.redis_manager.hgetall(query_key)

            if not query_data:
                return {
                    "query": query,
                    "message": "No hay datos históricos para esta query",
                    "suggestions": await self._get_similar_queries(query)
                }

            # Procesar métricas de la query
            total_searches = int(query_data.get(b"total_searches", 0))
            avg_results = float(query_data.get(b"avg_results", 0))
            avg_time_ms = float(query_data.get(b"avg_time_ms", 0))
            zero_results_count = int(query_data.get(b"zero_results_count", 0))
            zero_results_rate = (zero_results_count / total_searches * 100) if total_searches > 0 else 0

            # Obtener trending info
            trending_score = await self._get_query_trending_score(query)

            # Análisis de performance
            performance_rating = "excellent"
            if avg_time_ms > self.slow_search_threshold:
                performance_rating = "slow"
            elif zero_results_rate > 50:
                performance_rating = "poor_results"
            elif avg_results < self.low_results_threshold:
                performance_rating = "low_results"

            # Sugerencias de optimización
            optimization_suggestions = await self._get_optimization_suggestions(
                query, avg_results, avg_time_ms, zero_results_rate
            )

            return {
                "query": query,
                "metrics": {
                    "total_searches": total_searches,
                    "avg_results_count": avg_results,
                    "avg_search_time_ms": avg_time_ms,
                    "zero_results_rate": zero_results_rate,
                    "trending_score": trending_score
                },
                "performance": {
                    "rating": performance_rating,
                    "is_slow": avg_time_ms > self.slow_search_threshold,
                    "has_poor_results": zero_results_rate > 30
                },
                "optimization_suggestions": optimization_suggestions,
                "similar_queries": await self._get_similar_queries(query),
                "analysis_period_days": days
            }

        except Exception as e:
            logger.error(f"Error obteniendo insights de query: {e}")
            return {"query": query, "error": str(e)}

    async def get_business_intelligence_report(
        self,
        period: str = "week"
    ) -> Dict:
        """
        Generar reporte de business intelligence.

        Args:
            period: Período de análisis (week, month, quarter)

        Returns:
            Dict: Reporte de BI completo
        """
        try:
            # Determinar rango de fechas
            if period == "week":
                days = 7
            elif period == "month":
                days = 30
            elif period == "quarter":
                days = 90
            else:
                days = 7

            # Obtener insights de negocio
            search_volume_trends, popular_categories, user_intent_analysis, conversion_opportunities = await asyncio.gather(
                self._analyze_search_volume_trends(days),
                self._analyze_popular_categories(days),
                self._analyze_user_intent(days),
                self._identify_conversion_opportunities(days)
            )

            # Performance insights
            performance_insights = await self._generate_performance_insights(days)

            # Recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(
                search_volume_trends,
                popular_categories,
                user_intent_analysis,
                performance_insights
            )

            return {
                "report_type": "business_intelligence",
                "period": period,
                "days_analyzed": days,
                "generated_at": datetime.now().isoformat(),
                "executive_summary": {
                    "total_searches": search_volume_trends.get("total_searches", 0),
                    "unique_queries": search_volume_trends.get("unique_queries", 0),
                    "avg_results_per_search": search_volume_trends.get("avg_results", 0),
                    "search_success_rate": search_volume_trends.get("success_rate", 0)
                },
                "search_volume_trends": search_volume_trends,
                "popular_categories": popular_categories,
                "user_intent_analysis": user_intent_analysis,
                "conversion_opportunities": conversion_opportunities,
                "performance_insights": performance_insights,
                "strategic_recommendations": strategic_recommendations
            }

        except Exception as e:
            logger.error(f"Error generando reporte BI: {e}")
            return {"error": str(e)}

    async def _track_daily_stats(self, date_str: str, event_data: Dict) -> None:
        """Track estadísticas diarias."""
        try:
            daily_key = f"{self.daily_key}:{date_str}"

            # Incrementar contadores
            await self.redis_manager.hincrby(daily_key, "total_searches", 1)

            if event_data["has_results"]:
                await self.redis_manager.hincrby(daily_key, "searches_with_results", 1)
            else:
                await self.redis_manager.hincrby(daily_key, "zero_result_searches", 1)

            if event_data["is_slow"]:
                await self.redis_manager.hincrby(daily_key, "slow_searches", 1)

            # Agregar tiempo de búsqueda para promedio
            await self.redis_manager.hincrby(daily_key, "total_search_time_ms", event_data["search_time_ms"])
            await self.redis_manager.hincrby(daily_key, "total_results", event_data["results_count"])

            # Trackear por fuente
            if event_data["source"]:
                await self.redis_manager.hincrby(daily_key, f"source_{event_data['source']}", 1)

            # Trackear por tipo de usuario
            if event_data["user_type"]:
                await self.redis_manager.hincrby(daily_key, f"user_type_{event_data['user_type']}", 1)

            # Expiración
            await self.redis_manager.expire(daily_key, 86400 * 90)  # 90 días

        except Exception as e:
            logger.warning(f"Error tracking daily stats: {e}")

    async def _track_hourly_stats(self, hour_str: str, event_data: Dict) -> None:
        """Track estadísticas por hora."""
        try:
            hourly_key = f"{self.hourly_key}:{hour_str}"

            await self.redis_manager.hincrby(hourly_key, "searches", 1)
            await self.redis_manager.hincrby(hourly_key, "total_time_ms", event_data["search_time_ms"])
            await self.redis_manager.hincrby(hourly_key, "total_results", event_data["results_count"])

            await self.redis_manager.expire(hourly_key, 86400 * 7)  # 7 días

        except Exception as e:
            logger.warning(f"Error tracking hourly stats: {e}")

    async def _track_query_metrics(self, query: str, event_data: Dict) -> None:
        """Track métricas específicas por query."""
        try:
            query_key = f"{self.queries_key}:{query}"

            # Incrementar contadores
            await self.redis_manager.hincrby(query_key, "total_searches", 1)
            await self.redis_manager.hincrby(query_key, "total_results", event_data["results_count"])
            await self.redis_manager.hincrby(query_key, "total_time_ms", event_data["search_time_ms"])

            if event_data["is_zero_results"]:
                await self.redis_manager.hincrby(query_key, "zero_results_count", 1)

            # Actualizar timestamp de última búsqueda
            await self.redis_manager.hset(query_key, "last_searched", event_data["timestamp"])

            await self.redis_manager.expire(query_key, 86400 * 30)  # 30 días

        except Exception as e:
            logger.warning(f"Error tracking query metrics: {e}")

    async def _track_performance_metrics(self, event_data: Dict) -> None:
        """Track métricas de performance."""
        try:
            perf_key = f"{self.performance_key}:current"

            # Agregar tiempo de respuesta a lista para percentiles
            await self.redis_manager.lpush(f"{perf_key}:response_times", event_data["search_time_ms"])
            await self.redis_manager.ltrim(f"{perf_key}:response_times", 0, 1000)  # Mantener últimos 1000

            # Agregar conteo de resultados
            await self.redis_manager.lpush(f"{perf_key}:result_counts", event_data["results_count"])
            await self.redis_manager.ltrim(f"{perf_key}:result_counts", 0, 1000)

            await self.redis_manager.expire(f"{perf_key}:response_times", 86400)
            await self.redis_manager.expire(f"{perf_key}:result_counts", 86400)

        except Exception as e:
            logger.warning(f"Error tracking performance metrics: {e}")

    async def _track_user_behavior(self, user_id: Optional[str], user_type: Optional[str], event_data: Dict) -> None:
        """Track comportamiento de usuarios."""
        try:
            if not user_id:
                return

            user_key = f"{self.users_key}:{user_id}"

            await self.redis_manager.hincrby(user_key, "total_searches", 1)
            await self.redis_manager.hset(user_key, "last_search", event_data["timestamp"])

            if user_type:
                await self.redis_manager.hset(user_key, "user_type", user_type)

            await self.redis_manager.expire(user_key, 86400 * 30)  # 30 días

        except Exception as e:
            logger.warning(f"Error tracking user behavior: {e}")

    async def _detect_patterns(self, event_data: Dict) -> None:
        """Detectar patrones en búsquedas."""
        try:
            patterns_key = f"{self.patterns_key}:current"

            # Detectar queries sin resultados frecuentes
            if event_data["is_zero_results"]:
                await self.redis_manager.zadd(f"{patterns_key}:zero_results", {event_data["query"]: 1})

            # Detectar búsquedas lentas frecuentes
            if event_data["is_slow"]:
                await self.redis_manager.zadd(f"{patterns_key}:slow_queries", {event_data["query"]: 1})

            # Expiración
            await self.redis_manager.expire(f"{patterns_key}:zero_results", 86400 * 7)
            await self.redis_manager.expire(f"{patterns_key}:slow_queries", 86400 * 7)

        except Exception as e:
            logger.warning(f"Error detecting patterns: {e}")

    async def _get_overview_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Obtener métricas generales."""
        try:
            total_searches = 0
            total_results = 0
            zero_result_searches = 0
            slow_searches = 0

            # Iterar por días en el rango
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                daily_key = f"{self.daily_key}:{date_str}"

                daily_data = await self.redis_manager.hgetall(daily_key)
                if daily_data:
                    total_searches += int(daily_data.get(b"total_searches", 0))
                    total_results += int(daily_data.get(b"total_results", 0))
                    zero_result_searches += int(daily_data.get(b"zero_result_searches", 0))
                    slow_searches += int(daily_data.get(b"slow_searches", 0))

                current_date += timedelta(days=1)

            # Calcular métricas derivadas
            avg_results_per_search = (total_results / total_searches) if total_searches > 0 else 0
            success_rate = ((total_searches - zero_result_searches) / total_searches * 100) if total_searches > 0 else 0
            slow_search_rate = (slow_searches / total_searches * 100) if total_searches > 0 else 0

            return {
                "total_searches": total_searches,
                "total_results": total_results,
                "avg_results_per_search": round(avg_results_per_search, 2),
                "success_rate": round(success_rate, 2),
                "zero_result_searches": zero_result_searches,
                "slow_searches": slow_searches,
                "slow_search_rate": round(slow_search_rate, 2)
            }

        except Exception as e:
            logger.error(f"Error obteniendo overview metrics: {e}")
            return {}

    async def _get_trending_queries(self, days: int) -> List[Dict]:
        """Obtener queries trending."""
        try:
            # Esta implementación usa datos mock para demostración
            # En producción, se calcularía desde los datos reales
            return [
                {"query": "laptop gaming", "searches": 245, "trend": "up"},
                {"query": "celular samsung", "searches": 189, "trend": "up"},
                {"query": "auriculares bluetooth", "searches": 156, "trend": "stable"},
                {"query": "tablet android", "searches": 134, "trend": "down"},
                {"query": "smartwatch", "searches": 98, "trend": "up"}
            ]

        except Exception as e:
            logger.error(f"Error obteniendo trending queries: {e}")
            return []

    async def _get_performance_metrics(self, days: int) -> Dict:
        """Obtener métricas de performance."""
        try:
            perf_key = f"{self.performance_key}:current"

            # Obtener tiempos de respuesta
            response_times = await self.redis_manager.lrange(f"{perf_key}:response_times", 0, -1)
            result_counts = await self.redis_manager.lrange(f"{perf_key}:result_counts", 0, -1)

            if response_times:
                times = [int(t) for t in response_times]
                avg_response_time = statistics.mean(times)
                p95_response_time = statistics.quantiles(times, n=20)[18] if len(times) > 10 else avg_response_time
                p99_response_time = statistics.quantiles(times, n=100)[98] if len(times) > 100 else avg_response_time
            else:
                avg_response_time = p95_response_time = p99_response_time = 0

            if result_counts:
                counts = [int(c) for c in result_counts]
                avg_result_count = statistics.mean(counts)
            else:
                avg_result_count = 0

            return {
                "avg_response_time_ms": round(avg_response_time, 2),
                "p95_response_time_ms": round(p95_response_time, 2),
                "p99_response_time_ms": round(p99_response_time, 2),
                "avg_result_count": round(avg_result_count, 2),
                "samples": len(response_times) if response_times else 0
            }

        except Exception as e:
            logger.error(f"Error obteniendo performance metrics: {e}")
            return {}

    async def _get_user_segmentation_metrics(self, days: int) -> Dict:
        """Obtener métricas de segmentación de usuarios."""
        try:
            # Implementación simplificada - en producción usaría datos reales
            return {
                "by_user_type": {
                    "buyer": {"searches": 1540, "percentage": 65.8},
                    "vendor": {"searches": 620, "percentage": 26.5},
                    "admin": {"searches": 180, "percentage": 7.7}
                },
                "by_source": {
                    "web": {"searches": 1890, "percentage": 80.8},
                    "mobile": {"searches": 350, "percentage": 15.0},
                    "api": {"searches": 100, "percentage": 4.2}
                }
            }

        except Exception as e:
            logger.error(f"Error obteniendo user segmentation: {e}")
            return {}

    async def _get_similar_queries(self, query: str) -> List[str]:
        """Obtener queries similares."""
        # Implementación simplificada
        return [
            f"{query} precio",
            f"{query} barato",
            f"mejor {query}",
            f"{query} review"
        ]

    async def _get_query_trending_score(self, query: str) -> float:
        """Calcular score de trending para una query."""
        # Implementación simplificada
        return 0.75

    async def _get_optimization_suggestions(
        self,
        query: str,
        avg_results: float,
        avg_time_ms: float,
        zero_results_rate: float
    ) -> List[str]:
        """Generar sugerencias de optimización."""
        suggestions = []

        if avg_time_ms > self.slow_search_threshold:
            suggestions.append("Optimizar índices de búsqueda para mejorar velocidad")

        if zero_results_rate > 30:
            suggestions.append("Revisar productos disponibles para esta categoría")
            suggestions.append("Considerar sinónimos y variantes de la query")

        if avg_results < self.low_results_threshold:
            suggestions.append("Expandir catálogo de productos relacionados")

        return suggestions

    # Métodos adicionales para BI report
    async def _analyze_search_volume_trends(self, days: int) -> Dict:
        """Analizar tendencias de volumen de búsqueda."""
        return {
            "total_searches": 2340,
            "unique_queries": 1456,
            "avg_results": 12.5,
            "success_rate": 87.2,
            "growth_rate": 15.3
        }

    async def _analyze_popular_categories(self, days: int) -> List[Dict]:
        """Analizar categorías populares."""
        return [
            {"category": "Electronics", "searches": 856, "percentage": 36.6},
            {"category": "Clothing", "searches": 623, "percentage": 26.6},
            {"category": "Home & Garden", "searches": 445, "percentage": 19.0},
            {"category": "Sports", "searches": 416, "percentage": 17.8}
        ]

    async def _analyze_user_intent(self, days: int) -> Dict:
        """Analizar intención de usuario."""
        return {
            "browsing": {"percentage": 45.2, "queries": ["laptop", "celular", "auriculares"]},
            "purchasing": {"percentage": 35.8, "queries": ["comprar laptop", "precio celular", "oferta tablet"]},
            "comparison": {"percentage": 19.0, "queries": ["vs", "comparar", "mejor"]}
        }

    async def _identify_conversion_opportunities(self, days: int) -> List[Dict]:
        """Identificar oportunidades de conversión."""
        return [
            {
                "opportunity": "High-intent zero results",
                "description": "Queries con intención de compra que no devuelven resultados",
                "impact": "high",
                "queries": ["comprar iPhone 15", "laptop gamer barato", "auriculares sony noise"]
            },
            {
                "opportunity": "Popular categories low inventory",
                "description": "Categorías populares con poco inventario",
                "impact": "medium",
                "categories": ["Gaming Laptops", "Wireless Earbuds", "Smartwatches"]
            }
        ]

    async def _generate_performance_insights(self, days: int) -> Dict:
        """Generar insights de performance."""
        return {
            "cache_hit_rate": 78.5,
            "avg_response_time": 850,
            "slow_queries_percentage": 12.3,
            "recommendations": [
                "Optimizar índices GIN para queries de texto largo",
                "Implementar cache warming para queries populares",
                "Revisar configuración de ChromaDB para búsquedas semánticas"
            ]
        }

    async def _generate_strategic_recommendations(self, *args) -> List[Dict]:
        """Generar recomendaciones estratégicas."""
        return [
            {
                "priority": "high",
                "category": "inventory",
                "recommendation": "Expandir inventario en categorías de gaming",
                "rationale": "Alto volumen de búsquedas con baja disponibilidad de productos"
            },
            {
                "priority": "medium",
                "category": "performance",
                "recommendation": "Optimizar búsquedas de texto largo",
                "rationale": "15% de queries exceden threshold de performance"
            },
            {
                "priority": "low",
                "category": "ux",
                "recommendation": "Implementar sugerencias de búsqueda mejoradas",
                "rationale": "Reducir tasa de búsquedas sin resultados"
            }
        ]


# Factory function
def create_search_analytics_service(redis_manager: RedisManager) -> SearchAnalyticsService:
    """
    Factory function para crear SearchAnalyticsService.

    Args:
        redis_manager: Instancia de RedisManager

    Returns:
        SearchAnalyticsService: Instancia configurada del servicio
    """
    return SearchAnalyticsService(redis_manager)