# ~/app/utils/benchmark.py
# ---------------------------------------------------------------------------------------------
# MeStore - Benchmark Tools for Database Performance
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
"""
Benchmark Tools - Herramientas especializadas para benchmarking de database performance

Características principales:
- Benchmark automático de endpoints críticos (auth, embeddings)
- Análisis de regresión de performance entre versiones
- Simulación de carga para detectar cuellos de botella
- Comparación de performance antes/después de optimizaciones
- Generación de reportes detallados con métricas clave
"""

import asyncio
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from contextlib import asynccontextmanager

import httpx
from sqlalchemy import text
from loguru import logger

from app.database import AsyncSessionLocal
from app.utils.query_analyzer import query_analyzer


class DatabaseBenchmark:
    """Herramientas de benchmark para performance de base de datos."""

    def __init__(self):
        """Inicializar benchmark tools."""
        self.results_history: List[Dict] = []

    async def benchmark_crud_operations(
        self,
        table_name: str,
        operations: Optional[List[str]] = None,
        iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Benchmark completo de operaciones CRUD para una tabla.

        Args:
            table_name: Nombre de la tabla a testear
            operations: Lista de operaciones ['select', 'insert', 'update', 'delete']
            iterations: Número de iteraciones por operación

        Returns:
            Reporte completo de benchmark CRUD
        """
        if operations is None:
            operations = ['select_all', 'select_by_id', 'count', 'select_with_join']

        logger.info(f"Starting CRUD benchmark for {table_name} - {iterations} iterations")

        benchmark_results = {
            'table_name': table_name,
            'timestamp': datetime.now().isoformat(),
            'iterations': iterations,
            'operations': {},
            'summary': {}
        }

        async with AsyncSessionLocal() as session:
            for operation in operations:
                logger.info(f"Benchmarking {operation} on {table_name}")

                query, params = self._get_crud_query(table_name, operation)
                if not query:
                    continue

                # Ejecutar benchmark para esta operación
                operation_results = await self._benchmark_single_operation(
                    session, query, params, f"{table_name}_{operation}", iterations
                )

                benchmark_results['operations'][operation] = operation_results

        # Generar resumen
        benchmark_results['summary'] = self._generate_crud_summary(benchmark_results['operations'])

        # Guardar en historial
        self.results_history.append(benchmark_results)

        return benchmark_results

    def _get_crud_query(self, table_name: str, operation: str) -> Tuple[Optional[str], Dict]:
        """Generar query SQL para operación CRUD específica."""

        # Mapeo de nombres de tabla (singular a plural)
        table_mapping = {
            'user': 'users',
            'product': 'products', 
            'transaction': 'transactions',
            'inventory': 'inventory',
            'storage': 'storage'
        }

        table_plural = table_mapping.get(table_name.lower(), f"{table_name.lower()}s")

        queries = {
            'select_all': (f"SELECT * FROM {table_plural} LIMIT 50", {}),
            'select_by_id': (f"SELECT * FROM {table_plural} ORDER BY id LIMIT 1", {}),
            'count': (f"SELECT COUNT(*) FROM {table_plural}", {}),
            'select_with_join': self._get_join_query(table_name, table_plural),
            'select_with_filter': (
                f"SELECT * FROM {table_plural} WHERE created_at >= %(date)s LIMIT 20",
                {'date': '2024-01-01'}
            ),
            'select_paginated': (
                f"SELECT * FROM {table_plural} ORDER BY id LIMIT 20 OFFSET %(offset)s",
                {'offset': 0}
            )
        }

        return queries.get(operation, (None, {}))

    def _get_join_query(self, table_name: str, table_plural: str) -> Tuple[str, Dict]:
        """Generar query con JOIN específica para cada tabla."""

        join_queries = {
            'products': (
                "SELECT p.*, u.nombre as vendedor_nombre FROM products p "
                "JOIN users u ON p.vendedor_id = u.id LIMIT 20",
                {}
            ),
            'transactions': (
                "SELECT t.*, uc.nombre as comprador, uv.nombre as vendedor FROM transactions t "
                "JOIN users uc ON t.comprador_id = uc.id "
                "JOIN users uv ON t.vendedor_id = uv.id LIMIT 20",
                {}
            ),
            'inventory': (
                "SELECT i.*, p.nombre as producto_nombre FROM inventory i "
                "JOIN products p ON i.product_id = p.id LIMIT 20",
                {}
            ),
            'storage': (
                "SELECT s.*, u.nombre as propietario FROM storage s "
                "JOIN users u ON s.user_id = u.id LIMIT 20",
                {}
            )
        }

        return join_queries.get(table_plural, (f"SELECT * FROM {table_plural} ORDER BY id LIMIT 20", {}))

    async def _benchmark_single_operation(
        self,
        session,
        query: str,
        params: Dict,
        operation_name: str,
        iterations: int
    ) -> Dict[str, Any]:
        """Benchmark de una operación individual."""

        times = []
        errors = []

        for i in range(iterations):
            try:
                start_time = time.time()
                result = await session.execute(text(query), params)

                # Fetch results para simular uso real
                if result.returns_rows:
                    _ = result.fetchall()

                execution_time = time.time() - start_time
                times.append(execution_time)

            except Exception as e:
                errors.append({
                    'iteration': i,
                    'error': str(e),
                    'timestamp': time.time()
                })

        # Calcular estadísticas
        if times:
            return {
                'operation_name': operation_name,
                'iterations': iterations,
                'successful_iterations': len(times),
                'failed_iterations': len(errors),
                'avg_time': statistics.mean(times),
                'median_time': statistics.median(times),
                'min_time': min(times),
                'max_time': max(times),
                'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
                'percentile_95': self._percentile(times, 95),
                'percentile_99': self._percentile(times, 99),
                'times': times,
                'errors': errors
            }
        else:
            return {
                'operation_name': operation_name,
                'error': 'All iterations failed',
                'failed_iterations': len(errors),
                'errors': errors
            }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calcular percentil de una lista de datos."""
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)

        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def _generate_crud_summary(self, operations: Dict) -> Dict[str, Any]:
        """Generar resumen de benchmark CRUD."""
        successful_ops = {k: v for k, v in operations.items() if 'avg_time' in v}

        if not successful_ops:
            return {'status': 'all_operations_failed', 'total_operations': len(operations)}

        all_times = []
        for op_result in successful_ops.values():
            all_times.extend(op_result.get('times', []))

        slowest_op = max(successful_ops.items(), key=lambda x: x[1]['avg_time'])
        fastest_op = min(successful_ops.items(), key=lambda x: x[1]['avg_time'])

        return {
            'total_operations': len(operations),
            'successful_operations': len(successful_ops),
            'failed_operations': len(operations) - len(successful_ops),
            'overall_avg_time': statistics.mean(all_times) if all_times else 0,
            'overall_median_time': statistics.median(all_times) if all_times else 0,
            'slowest_operation': {
                'name': slowest_op[0],
                'avg_time': slowest_op[1]['avg_time']
            },
            'fastest_operation': {
                'name': fastest_op[0], 
                'avg_time': fastest_op[1]['avg_time']
            },
            'performance_grade': self._calculate_performance_grade(all_times)
        }

    def _calculate_performance_grade(self, times: List[float]) -> str:
        """Calcular grado de performance basado en tiempos."""
        if not times:
            return 'N/A'

        avg_time = statistics.mean(times)
        p95_time = self._percentile(times, 95)

        # Criterios de grading
        if avg_time < 0.01 and p95_time < 0.05:
            return 'A+ (Excellent)'
        elif avg_time < 0.05 and p95_time < 0.1:
            return 'A (Very Good)'
        elif avg_time < 0.1 and p95_time < 0.25:
            return 'B (Good)'
        elif avg_time < 0.5 and p95_time < 1.0:
            return 'C (Fair)'
        else:
            return 'D (Needs Optimization)'

    async def benchmark_endpoint_performance(
        self,
        base_url: str,
        endpoints_config: List[Dict[str, Any]],
        concurrent_requests: int = 10,
        total_requests: int = 100
    ) -> Dict[str, Any]:
        """
        Benchmark de performance de endpoints HTTP.

        Args:
            base_url: URL base de la API (ej: http://localhost:8000)
            endpoints_config: Lista de configs de endpoint con url, method, headers, body
            concurrent_requests: Número de requests concurrentes
            total_requests: Total de requests por endpoint

        Returns:
            Reporte de benchmark de endpoints
        """
        logger.info(f"Starting endpoint benchmark - {concurrent_requests} concurrent, {total_requests} total requests per endpoint")

        benchmark_results = {
            'base_url': base_url,
            'timestamp': datetime.now().isoformat(),
            'config': {
                'concurrent_requests': concurrent_requests,
                'total_requests': total_requests
            },
            'endpoints': {},
            'summary': {}
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint_config in endpoints_config:
                endpoint_name = endpoint_config.get('name', endpoint_config['url'])
                logger.info(f"Benchmarking endpoint: {endpoint_name}")

                endpoint_results = await self._benchmark_single_endpoint(
                    client, base_url, endpoint_config, concurrent_requests, total_requests
                )

                benchmark_results['endpoints'][endpoint_name] = endpoint_results

        # Generar resumen
        benchmark_results['summary'] = self._generate_endpoint_summary(benchmark_results['endpoints'])

        return benchmark_results

    async def _benchmark_single_endpoint(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        endpoint_config: Dict[str, Any],
        concurrent_requests: int,
        total_requests: int
    ) -> Dict[str, Any]:
        """Benchmark de un endpoint individual."""

        url = f"{base_url.rstrip('/')}{endpoint_config['url']}"
        method = endpoint_config.get('method', 'GET')
        headers = endpoint_config.get('headers', {})
        json_body = endpoint_config.get('json', None)

        # Dividir requests en batches concurrentes
        requests_per_batch = concurrent_requests
        num_batches = total_requests // requests_per_batch
        remaining_requests = total_requests % requests_per_batch

        all_times = []
        all_status_codes = []
        errors = []

        # Ejecutar batches
        for batch in range(num_batches):
            batch_times, batch_statuses, batch_errors = await self._execute_concurrent_requests(
                client, url, method, headers, json_body, requests_per_batch
            )

            all_times.extend(batch_times)
            all_status_codes.extend(batch_statuses)
            errors.extend(batch_errors)

        # Ejecutar requests restantes
        if remaining_requests > 0:
            batch_times, batch_statuses, batch_errors = await self._execute_concurrent_requests(
                client, url, method, headers, json_body, remaining_requests
            )

            all_times.extend(batch_times)
            all_status_codes.extend(batch_statuses)
            errors.extend(batch_errors)

        # Calcular estadísticas
        successful_requests = len([s for s in all_status_codes if 200 <= s < 300])

        return {
            'url': url,
            'method': method,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': len(errors),
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'avg_response_time': statistics.mean(all_times) if all_times else 0,
            'median_response_time': statistics.median(all_times) if all_times else 0,
            'min_response_time': min(all_times) if all_times else 0,
            'max_response_time': max(all_times) if all_times else 0,
            'percentile_95': self._percentile(all_times, 95),
            'percentile_99': self._percentile(all_times, 99),
            'requests_per_second': len(all_times) / sum(all_times) if sum(all_times) > 0 else 0,
            'status_codes_distribution': self._count_status_codes(all_status_codes),
            'errors': errors[:10]  # Solo primeros 10 errores
        }

    async def _execute_concurrent_requests(
        self,
        client: httpx.AsyncClient,
        url: str,
        method: str,
        headers: Dict,
        json_body: Optional[Dict],
        num_requests: int
    ) -> Tuple[List[float], List[int], List[Dict]]:
        """Ejecutar requests concurrentes y medir performance."""

        async def single_request():
            start_time = time.time()
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_body
                )

                response_time = time.time() - start_time
                return response_time, response.status_code, None

            except Exception as e:
                response_time = time.time() - start_time
                return response_time, 0, {
                    'error': str(e),
                    'timestamp': time.time()
                }

        # Ejecutar todas las requests concurrentemente
        tasks = [single_request() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        times = []
        status_codes = []
        errors = []

        for result in results:
            if isinstance(result, Exception):
                errors.append({
                    'error': str(result),
                    'timestamp': time.time()
                })
            else:
                response_time, status_code, error = result
                times.append(response_time)

                if error:
                    errors.append(error)
                    status_codes.append(0)
                else:
                    status_codes.append(status_code)

        return times, status_codes, errors

    def _count_status_codes(self, status_codes: List[int]) -> Dict[str, int]:
        """Contar distribución de códigos de estado."""
        distribution = {}
        for code in status_codes:
            code_str = str(code) if code != 0 else 'error'
            distribution[code_str] = distribution.get(code_str, 0) + 1
        return distribution

    def _generate_endpoint_summary(self, endpoints: Dict) -> Dict[str, Any]:
        """Generar resumen de benchmark de endpoints."""
        if not endpoints:
            return {'status': 'no_endpoints_tested'}

        all_response_times = []
        total_requests = 0
        successful_requests = 0

        for endpoint_result in endpoints.values():
            if 'avg_response_time' in endpoint_result:
                # Estimar tiempos individuales basados en estadísticas
                avg_time = endpoint_result['avg_response_time']
                num_requests = endpoint_result.get('successful_requests', 0)
                all_response_times.extend([avg_time] * num_requests)

            total_requests += endpoint_result.get('total_requests', 0)
            successful_requests += endpoint_result.get('successful_requests', 0)

        slowest_endpoint = max(endpoints.items(), 
                             key=lambda x: x[1].get('avg_response_time', 0))
        fastest_endpoint = min(endpoints.items(), 
                             key=lambda x: x[1].get('avg_response_time', float('inf')))

        return {
            'total_endpoints': len(endpoints),
            'total_requests': total_requests,
            'overall_success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'overall_avg_response_time': statistics.mean(all_response_times) if all_response_times else 0,
            'slowest_endpoint': {
                'name': slowest_endpoint[0],
                'avg_time': slowest_endpoint[1].get('avg_response_time', 0),
                'success_rate': slowest_endpoint[1].get('success_rate', 0)
            },
            'fastest_endpoint': {
                'name': fastest_endpoint[0],
                'avg_time': fastest_endpoint[1].get('avg_response_time', 0),
                'success_rate': fastest_endpoint[1].get('success_rate', 0)
            }
        }

    async def compare_performance_over_time(
        self,
        table_name: str,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """Comparar performance histórica de una tabla."""

        # Filtrar resultados históricos para esta tabla
        historical_results = [
            r for r in self.results_history
            if r.get('table_name') == table_name and 
            (datetime.now() - datetime.fromisoformat(r['timestamp'])).days <= days_back
        ]

        if len(historical_results) < 2:
            # Ejecutar nuevo benchmark para comparación
            logger.info(f"Insufficient historical data for {table_name}, running new benchmark")
            new_result = await self.benchmark_crud_operations(table_name)
            return {
                'table_name': table_name,
                'comparison': 'insufficient_data',
                'latest_result': new_result,
                'recommendation': 'Run benchmarks regularly to enable trend analysis'
            }

        # Analizar tendencias
        latest_result = max(historical_results, key=lambda x: x['timestamp'])
        oldest_result = min(historical_results, key=lambda x: x['timestamp'])

        comparison = self._analyze_performance_trend(oldest_result, latest_result)

        return {
            'table_name': table_name,
            'time_period': f'{days_back} days',
            'total_benchmarks': len(historical_results),
            'oldest_benchmark': oldest_result['timestamp'],
            'latest_benchmark': latest_result['timestamp'],
            'comparison': comparison,
            'trend_analysis': self._calculate_trend_metrics(historical_results)
        }

    def _analyze_performance_trend(self, old_result: Dict, new_result: Dict) -> Dict[str, Any]:
        """Analizar tendencia de performance entre dos resultados."""

        old_summary = old_result.get('summary', {})
        new_summary = new_result.get('summary', {})

        old_avg = old_summary.get('overall_avg_time', 0)
        new_avg = new_summary.get('overall_avg_time', 0)

        if old_avg == 0:
            return {'status': 'cannot_compare', 'reason': 'old_result_invalid'}

        improvement_pct = ((old_avg - new_avg) / old_avg) * 100

        status = 'stable'
        if improvement_pct > 10:
            status = 'improved'
        elif improvement_pct < -10:
            status = 'degraded'

        return {
            'status': status,
            'old_avg_time': old_avg,
            'new_avg_time': new_avg,
            'improvement_percentage': improvement_pct,
            'recommendation': self._get_trend_recommendation(status, improvement_pct)
        }

    def _get_trend_recommendation(self, status: str, improvement_pct: float) -> str:
        """Obtener recomendación basada en tendencia."""

        if status == 'improved':
            return f'Performance improved by {improvement_pct:.1f}% - maintain current optimizations'
        elif status == 'degraded':
            return f'Performance degraded by {abs(improvement_pct):.1f}% - investigate recent changes'
        else:
            return 'Performance is stable - continue regular monitoring'

    def _calculate_trend_metrics(self, results: List[Dict]) -> Dict[str, Any]:
        """Calcular métricas de tendencia histórica."""

        times = []
        timestamps = []

        for result in sorted(results, key=lambda x: x['timestamp']):
            summary = result.get('summary', {})
            avg_time = summary.get('overall_avg_time', 0)
            if avg_time > 0:
                times.append(avg_time)
                timestamps.append(result['timestamp'])

        if len(times) < 2:
            return {'status': 'insufficient_data'}

        # Calcular tendencia simple (regresión lineal básica)
        n = len(times)
        x_vals = list(range(n))

        # Pendiente = (n*Σxy - ΣxΣy) / (n*Σx² - (Σx)²)
        sum_x = sum(x_vals)
        sum_y = sum(times)
        sum_xy = sum(x * y for x, y in zip(x_vals, times))
        sum_x2 = sum(x * x for x in x_vals)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

        trend = 'stable'
        if slope > 0.001:
            trend = 'increasing'
        elif slope < -0.001:
            trend = 'decreasing'

        return {
            'trend': trend,
            'slope': slope,
            'data_points': n,
            'time_range': f"{timestamps[0]} to {timestamps[-1]}",
            'min_time': min(times),
            'max_time': max(times),
            'avg_time': statistics.mean(times)
        }


# Instancia global del benchmark
db_benchmark = DatabaseBenchmark()


# Funciones de conveniencia
async def quick_crud_benchmark(table_name: str) -> Dict[str, Any]:
    """Función rápida para benchmark CRUD de una tabla."""
    return await db_benchmark.benchmark_crud_operations(table_name, iterations=50)


async def quick_endpoint_benchmark(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Función rápida para benchmark de endpoints críticos."""

    endpoints_config = [
        {
            'name': 'health_check',
            'url': '/api/v1/health',
            'method': 'GET'
        },
        {
            'name': 'health_complete',
            'url': '/api/v1/health/complete',
            'method': 'GET'
        },
        {
            'name': 'products_list',
            'url': '/api/v1/products/?limit=20',
            'method': 'GET'
        }
    ]

    return await db_benchmark.benchmark_endpoint_performance(
        base_url, endpoints_config, concurrent_requests=5, total_requests=50
    )