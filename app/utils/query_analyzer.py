# ~/app/utils/query_analyzer.py
# ---------------------------------------------------------------------------------------------
# MeStore - Query Analyzer with EXPLAIN Support
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
"""
Query Analyzer - Sistema completo de análisis EXPLAIN para PostgreSQL Async

Características principales:
- EXPLAIN ANALYZE automático para queries críticas
- Detección de N+1 queries en relaciones complejas
- Benchmarking de endpoints con métricas detalladas
- Análisis de uso de índices en tiempo real
- Logger de queries lentas con análisis automático
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database import AsyncSessionLocal


class QueryAnalyzer:
    """Analizador de queries con soporte EXPLAIN ANALYZE para PostgreSQL async."""

    def __init__(self, slow_query_threshold: float = 0.1):
        """
        Inicializar analizador de queries.

        Args:
            slow_query_threshold: Tiempo en segundos para considerar query lenta
        """
        self.slow_query_threshold = slow_query_threshold
        self.query_stats: Dict[str, List[Dict]] = {}

    async def analyze_query(
        self,
        session: AsyncSession,
        query: str,
        params: Optional[Dict] = None,
        query_name: str = "unnamed_query"
    ) -> Dict[str, Any]:
        """
        Analizar query con EXPLAIN ANALYZE.

        Args:
            session: Sesión async de SQLAlchemy
            query: Query SQL a analizar
            params: Parámetros de la query
            query_name: Nombre identificativo de la query

        Returns:
            Dict con análisis completo: tiempo, plan, métricas
        """
        start_time = time.time()

        try:
            # 1. Ejecutar EXPLAIN ANALYZE
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            explain_result = await session.execute(text(explain_query), params or {})
            explain_data = explain_result.fetchone()[0]

            # 2. Ejecutar query real para timing
            query_result = await session.execute(text(query), params or {})
            execution_time = time.time() - start_time

            # 3. Extraer métricas del plan
            plan_metrics = self._extract_plan_metrics(explain_data[0])

            # 4. Crear análisis completo
            analysis = {
                "query_name": query_name,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "query": query[:200] + "..." if len(query) > 200 else query,
                "plan_metrics": plan_metrics,
                "explain_plan": explain_data[0],
                "is_slow": execution_time > self.slow_query_threshold,
                "index_usage": self._analyze_index_usage(explain_data[0]),
                "recommendations": self._generate_recommendations(plan_metrics, execution_time)
            }

            # 5. Registrar en estadísticas
            self._record_query_stats(query_name, analysis)

            # 6. Log si es query lenta
            if analysis["is_slow"]:
                logger.warning(f"Slow query detected: {query_name} - {execution_time:.3f}s")

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing query {query_name}: {e}")
            return {
                "query_name": query_name,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }

    def _extract_plan_metrics(self, plan: Dict) -> Dict[str, Any]:
        """Extraer métricas clave del plan de ejecución."""
        return {
            "total_cost": plan.get("Total Cost", 0),
            "actual_time": plan.get("Actual Total Time", 0),
            "actual_rows": plan.get("Actual Rows", 0),
            "planned_rows": plan.get("Plan Rows", 0),
            "node_type": plan.get("Node Type", "Unknown"),
            "shared_hit_blocks": plan.get("Shared Hit Blocks", 0),
            "shared_read_blocks": plan.get("Shared Read Blocks", 0),
            "temp_read_blocks": plan.get("Temp Read Blocks", 0),
            "temp_written_blocks": plan.get("Temp Written Blocks", 0)
        }

    def _analyze_index_usage(self, plan: Dict) -> Dict[str, Any]:
        """Analizar uso de índices en el plan."""
        index_usage = {
            "indexes_used": [],
            "sequential_scans": 0,
            "index_scans": 0,
            "bitmap_scans": 0
        }

        def analyze_node(node):
            node_type = node.get("Node Type", "")

            if "Index" in node_type:
                index_usage["index_scans"] += 1
                if "Index Name" in node:
                    index_usage["indexes_used"].append(node["Index Name"])
            elif "Seq Scan" in node_type:
                index_usage["sequential_scans"] += 1
            elif "Bitmap" in node_type:
                index_usage["bitmap_scans"] += 1

            # Recursivamente analizar sub-planes
            for child in node.get("Plans", []):
                analyze_node(child)

        analyze_node(plan)
        return index_usage

    def _generate_recommendations(self, metrics: Dict, execution_time: float) -> List[str]:
        """Generar recomendaciones basadas en métricas."""
        recommendations = []

        # Análisis de tiempo de ejecución
        if execution_time > 1.0:
            recommendations.append("Query muy lenta (>1s): considerar optimización urgente")
        elif execution_time > self.slow_query_threshold:
            recommendations.append("Query lenta: revisar índices y estructura")

        # Análisis de filas vs estimación
        actual_rows = metrics.get("actual_rows", 0)
        planned_rows = metrics.get("planned_rows", 0)

        if planned_rows > 0 and abs(actual_rows - planned_rows) / planned_rows > 0.5:
            recommendations.append("Estimación de filas imprecisa: actualizar estadísticas de tabla")

        # Análisis de I/O
        if metrics.get("temp_written_blocks", 0) > 0:
            recommendations.append("Uso de almacenamiento temporal: aumentar work_mem o optimizar query")

        if metrics.get("shared_read_blocks", 0) > metrics.get("shared_hit_blocks", 0) * 2:
            recommendations.append("Baja tasa de cache hit: considerar aumentar shared_buffers")

        return recommendations

    def _record_query_stats(self, query_name: str, analysis: Dict):
        """Registrar estadísticas de query para análisis posterior."""
        if query_name not in self.query_stats:
            self.query_stats[query_name] = []

        self.query_stats[query_name].append({
            "timestamp": analysis["timestamp"],
            "execution_time": analysis["execution_time"],
            "total_cost": analysis["plan_metrics"].get("total_cost", 0),
            "actual_rows": analysis["plan_metrics"].get("actual_rows", 0)
        })

        # Mantener solo últimas 100 ejecuciones por query
        self.query_stats[query_name] = self.query_stats[query_name][-100:]

    async def benchmark_endpoint_queries(
        self,
        endpoint_name: str,
        queries_to_test: List[Tuple[str, str, Optional[Dict]]],
        iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Hacer benchmark de múltiples queries de un endpoint.

        Args:
            endpoint_name: Nombre del endpoint (ej: 'auth_login')
            queries_to_test: Lista de (query_name, query_sql, params)
            iterations: Número de iteraciones para promedio

        Returns:
            Reporte completo de benchmark
        """
        benchmark_results = {
            "endpoint_name": endpoint_name,
            "iterations": iterations,
            "timestamp": datetime.now().isoformat(),
            "query_results": {},
            "summary": {}
        }

        async with self._get_session() as session:
            for query_name, query_sql, params in queries_to_test:
                logger.info(f"Benchmarking {query_name} for {endpoint_name}")

                query_times = []
                query_analyses = []

                for i in range(iterations):
                    analysis = await self.analyze_query(session, query_sql, params, query_name)
                    query_times.append(analysis.get("execution_time", 0))

                    if i == 0:  # Solo guardar análisis completo de la primera iteración
                        query_analyses.append(analysis)

                # Calcular estadísticas
                avg_time = sum(query_times) / len(query_times)
                min_time = min(query_times)
                max_time = max(query_times)

                benchmark_results["query_results"][query_name] = {
                    "average_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "times": query_times,
                    "analysis": query_analyses[0] if query_analyses else None
                }

        # Generar resumen
        all_times = [result["average_time"] for result in benchmark_results["query_results"].values()]
        benchmark_results["summary"] = {
            "total_queries": len(queries_to_test),
            "total_avg_time": sum(all_times),
            "slowest_query": max(benchmark_results["query_results"].items(), 
                                 key=lambda x: x[1]["average_time"]) if all_times else None,
            "fastest_query": min(benchmark_results["query_results"].items(), 
                                 key=lambda x: x[1]["average_time"]) if all_times else None
        }

        return benchmark_results

    @asynccontextmanager
    async def _get_session(self):
        """Context manager para sesiones async."""
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    async def detect_n_plus_one_queries(
        self,
        base_query: str,
        related_queries: List[str],
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Detectar patrones N+1 en queries relacionadas.

        Args:
            base_query: Query principal que obtiene registros padre
            related_queries: Lista de queries que se ejecutan por cada registro padre
            params: Parámetros para las queries

        Returns:
            Análisis de patrón N+1 y recomendaciones
        """
        async with self._get_session() as session:
            # Analizar query base
            base_analysis = await self.analyze_query(session, base_query, params, "base_query")
            base_rows = base_analysis["plan_metrics"].get("actual_rows", 0)

            # Simular N queries relacionadas
            total_related_time = 0
            related_analyses = []

            for i, related_query in enumerate(related_queries):
                analysis = await self.analyze_query(
                    session, related_query, params, f"related_query_{i}"
                )
                related_analyses.append(analysis)
                total_related_time += analysis.get("execution_time", 0)

            # Calcular impacto N+1
            estimated_n_plus_one_time = base_analysis.get("execution_time", 0) + (
                total_related_time * base_rows
            )

            return {
                "base_query_analysis": base_analysis,
                "related_queries_analysis": related_analyses,
                "base_rows": base_rows,
                "estimated_total_time": estimated_n_plus_one_time,
                "is_n_plus_one_issue": estimated_n_plus_one_time > 0.5,  # >500ms
                "recommendations": [
                    "Usar JOIN en lugar de queries separadas",
                    "Implementar eager loading con select_related",
                    "Considerar batch loading para relaciones"
                ] if estimated_n_plus_one_time > 0.5 else ["Performance aceptable"]
            }

    def get_query_statistics(self, query_name: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estadísticas de queries ejecutadas."""
        if query_name:
            return {
                "query_name": query_name,
                "executions": len(self.query_stats.get(query_name, [])),
                "stats": self.query_stats.get(query_name, [])
            }

        # Estadísticas generales
        total_executions = sum(len(stats) for stats in self.query_stats.values())

        return {
            "total_queries_tracked": len(self.query_stats),
            "total_executions": total_executions,
            "queries": {
                name: {
                    "executions": len(stats),
                    "avg_time": sum(s["execution_time"] for s in stats) / len(stats) if stats else 0,
                    "last_execution": stats[-1]["timestamp"] if stats else None
                }
                for name, stats in self.query_stats.items()
            }
        }


# Instancia global del analizador
query_analyzer = QueryAnalyzer()


# Funciones de conveniencia para uso directo
async def analyze_query_explain(
    query: str,
    params: Optional[Dict] = None,
    query_name: str = "ad_hoc_query"
) -> Dict[str, Any]:
    """Función de conveniencia para analizar una query directamente."""
    async with AsyncSessionLocal() as session:
        return await query_analyzer.analyze_query(session, query, params, query_name)


async def benchmark_crud_operations(model_name: str = "Product") -> Dict[str, Any]:
    """Benchmark de operaciones CRUD básicas."""
    crud_queries = [
        (f"{model_name.lower()}_select_all", f"SELECT * FROM {model_name.lower()}s LIMIT 10", None),
        (f"{model_name.lower()}_select_by_id", f"SELECT * FROM {model_name.lower()}s WHERE id = %(id)s", {"id": 1}),
        (f"{model_name.lower()}_count", f"SELECT COUNT(*) FROM {model_name.lower()}s", None),
    ]

    return await query_analyzer.benchmark_endpoint_queries(
        f"{model_name.lower()}_crud", crud_queries, iterations=5
    )
