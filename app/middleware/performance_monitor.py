# ~/app/middleware/performance_monitor.py
# ---------------------------------------------------------------------------------------------
# MeStore - Performance Monitor Middleware
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
"""
Performance Monitor Middleware - Monitoring en tiempo real de endpoints críticos

Características principales:
- Logging automático de performance por endpoint
- Detección de queries lentas en tiempo real
- Métricas de pool de conexiones
- Alertas automáticas para degradación de performance
- Integración con Query Analyzer para análisis profundo
"""

import time
import asyncio
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from app.utils.query_analyzer import query_analyzer
from app.core.database import engine


class PerformanceMonitorMiddleware(BaseHTTPMiddleware):
    """Middleware para monitoreo de performance en tiempo real."""

    def __init__(self, app, slow_endpoint_threshold: float = 1.0):
        """
        Inicializar middleware de performance.

        Args:
            app: Aplicación FastAPI
            slow_endpoint_threshold: Tiempo en segundos para considerar endpoint lento
        """
        super().__init__(app)
        self.slow_threshold = slow_endpoint_threshold
        self.endpoint_stats: Dict[str, list] = {}
        self.critical_endpoints = {
            '/api/v1/auth/login',
            '/api/v1/auth/register', 
            '/api/v1/embeddings/search',
            '/api/v1/embeddings/similarity',
            '/api/v1/health/complete',
            '/api/v1/products/',
            '/api/v1/users/'
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Procesar request con monitoring de performance."""
        start_time = time.time()
        endpoint = f"{request.method} {request.url.path}"

        # Obtener métricas del pool antes del request
        pool_stats_before = self._get_pool_stats()

        try:
            # Ejecutar request
            response = await call_next(request)

            # Calcular tiempo de respuesta
            process_time = time.time() - start_time

            # Obtener métricas del pool después del request
            pool_stats_after = self._get_pool_stats()

            # Crear métricas del request
            request_metrics = {
                'endpoint': endpoint,
                'method': request.method,
                'path': request.url.path,
                'process_time': process_time,
                'status_code': response.status_code,
                'timestamp': time.time(),
                'pool_before': pool_stats_before,
                'pool_after': pool_stats_after,
                'is_critical': self._is_critical_endpoint(request.url.path),
                'is_slow': process_time > self.slow_threshold
            }

            # Registrar métricas
            await self._record_metrics(request_metrics)

            # Agregar headers de performance
            response.headers['X-Process-Time'] = str(process_time)
            response.headers['X-Pool-Active'] = str(pool_stats_after.get('active', 0))

            # Log si es endpoint lento
            if request_metrics['is_slow']:
                logger.warning(
                    f"Slow endpoint detected: {endpoint} - {process_time:.3f}s"
                )

                # Si es endpoint crítico y muy lento, hacer análisis profundo
                if request_metrics['is_critical'] and process_time > 2.0:
                    asyncio.create_task(self._analyze_slow_endpoint(request, process_time))

            return response

        except Exception as e:
            process_time = time.time() - start_time

            # Log error con contexto de performance
            logger.error(
                f"Endpoint error: {endpoint} - {process_time:.3f}s - Error: {str(e)}"
            )

            # Registrar error en métricas
            error_metrics = {
                'endpoint': endpoint,
                'method': request.method,
                'path': request.url.path,
                'process_time': process_time,
                'status_code': 500,
                'timestamp': time.time(),
                'error': str(e),
                'is_critical': self._is_critical_endpoint(request.url.path)
            }

            await self._record_metrics(error_metrics)

            # Retornar error response
            return JSONResponse(
                status_code=500,
                content={'detail': 'Internal server error', 'process_time': process_time}
            )

    def _get_pool_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas actuales del pool de conexiones."""
        try:
            pool = engine.pool
            return {
                'size': getattr(pool, 'size', lambda: 0)(),
                'checked_in': getattr(pool, 'checkedin', lambda: 0)(),
                'checked_out': getattr(pool, 'checkedout', lambda: 0)(),
                'overflow': getattr(pool, 'overflow', lambda: 0)(),
                'invalid': getattr(pool, 'invalid', lambda: 0)(),
                'active': getattr(pool, 'checkedout', lambda: 0)()
            }
        except Exception as e:
            logger.warning(f"Error getting pool stats: {e}")
            return {'error': str(e)}

    def _is_critical_endpoint(self, path: str) -> bool:
        """Verificar si el endpoint es crítico."""
        return any(critical in path for critical in self.critical_endpoints)

    async def _record_metrics(self, metrics: Dict[str, Any]):
        """Registrar métricas del endpoint."""
        endpoint = metrics['endpoint']

        # Inicializar lista si no existe
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = []

        # Agregar métricas
        self.endpoint_stats[endpoint].append(metrics)

        # Mantener solo últimas 100 ejecuciones por endpoint
        self.endpoint_stats[endpoint] = self.endpoint_stats[endpoint][-100:]

        # Log métricas críticas
        if metrics['is_critical']:
            logger.info(
                f"Critical endpoint: {endpoint} - "
                f"{metrics['process_time']:.3f}s - "
                f"Status: {metrics['status_code']} - "
                f"Pool active: {metrics['pool_after'].get('active', 'N/A')}"
            )

    async def _analyze_slow_endpoint(self, request: Request, process_time: float):
        """Realizar análisis profundo de endpoint lento."""
        try:
            logger.info(f"Starting deep analysis for slow endpoint: {request.url.path}")

            # Analizar queries comunes para este endpoint
            if 'auth' in request.url.path:
                await self._analyze_auth_queries()
            elif 'embeddings' in request.url.path:
                await self._analyze_embeddings_queries()
            elif 'products' in request.url.path:
                await self._analyze_product_queries()
            elif 'users' in request.url.path:
                await self._analyze_user_queries()

        except Exception as e:
            logger.error(f"Error in deep analysis: {e}")

    async def _analyze_auth_queries(self):
        """Analizar queries típicas de autenticación."""
        auth_queries = [
            ('user_login_lookup', 'SELECT * FROM users WHERE email = %(email)s', {'email': 'test@example.com'}),
            ('user_permissions', 'SELECT * FROM users u LEFT JOIN user_roles ur ON u.id = ur.user_id WHERE u.id = %(user_id)s', {'user_id': 1})
        ]

        result = await query_analyzer.benchmark_endpoint_queries(
            'auth_endpoint', auth_queries, iterations=3
        )

        logger.info(f"Auth queries analysis: avg_time={result['summary'].get('total_avg_time', 0):.3f}s")

    async def _analyze_embeddings_queries(self):
        """Analizar queries típicas de embeddings."""
        embedding_queries = [
            ('vector_search', 'SELECT * FROM embeddings ORDER BY embedding <-> %(vector)s LIMIT 10', {'vector': '[0.1,0.2,0.3]'}),
            ('similarity_search', 'SELECT id, content, embedding <-> %(query_vector)s as distance FROM embeddings ORDER BY distance LIMIT 5', {'query_vector': '[0.1,0.2,0.3]'})
        ]

        result = await query_analyzer.benchmark_endpoint_queries(
            'embeddings_endpoint', embedding_queries, iterations=3
        )

        logger.info(f"Embeddings queries analysis: avg_time={result['summary'].get('total_avg_time', 0):.3f}s")

    async def _analyze_product_queries(self):
        """Analizar queries típicas de productos."""
        product_queries = [
            ('product_list_paginated', 'SELECT * FROM products WHERE active = true LIMIT 20 OFFSET %(offset)s', {'offset': 0}),
            ('product_with_vendor', 'SELECT p.*, u.nombre as vendor_name FROM products p JOIN users u ON p.vendedor_id = u.id WHERE p.id = %(product_id)s', {'product_id': 1}),
            ('product_inventory', 'SELECT p.*, i.cantidad FROM products p LEFT JOIN inventory i ON p.id = i.product_id WHERE p.id = %(product_id)s', {'product_id': 1})
        ]

        result = await query_analyzer.benchmark_endpoint_queries(
            'products_endpoint', product_queries, iterations=3
        )

        logger.info(f"Products queries analysis: avg_time={result['summary'].get('total_avg_time', 0):.3f}s")

    async def _analyze_user_queries(self):
        """Analizar queries típicas de usuarios."""
        user_queries = [
            ('user_profile', 'SELECT * FROM users WHERE id = %(user_id)s', {'user_id': 1}),
            ('user_products', 'SELECT COUNT(*) FROM products WHERE vendedor_id = %(user_id)s', {'user_id': 1}),
            ('user_transactions', 'SELECT * FROM transactions WHERE (comprador_id = %(user_id)s OR vendedor_id = %(user_id)s) ORDER BY created_at DESC LIMIT 10', {'user_id': 1})
        ]

        result = await query_analyzer.benchmark_endpoint_queries(
            'users_endpoint', user_queries, iterations=3
        )

        logger.info(f"Users queries analysis: avg_time={result['summary'].get('total_avg_time', 0):.3f}s")

    def get_endpoint_statistics(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estadísticas de endpoints monitoreados."""
        if endpoint:
            stats = self.endpoint_stats.get(endpoint, [])
            if not stats:
                return {'endpoint': endpoint, 'error': 'No data available'}

            times = [s['process_time'] for s in stats]
            status_codes = [s['status_code'] for s in stats]

            return {
                'endpoint': endpoint,
                'total_requests': len(stats),
                'avg_response_time': sum(times) / len(times),
                'min_response_time': min(times),
                'max_response_time': max(times),
                'success_rate': len([s for s in status_codes if 200 <= s < 300]) / len(status_codes),
                'slow_requests': len([t for t in times if t > self.slow_threshold]),
                'last_request': stats[-1]['timestamp'] if stats else None
            }

        # Estadísticas generales
        total_requests = sum(len(stats) for stats in self.endpoint_stats.values())
        all_times = []
        all_statuses = []

        for stats in self.endpoint_stats.values():
            all_times.extend([s['process_time'] for s in stats])
            all_statuses.extend([s['status_code'] for s in stats])

        critical_endpoints_stats = {}
        for endpoint in self.endpoint_stats:
            if any(critical in endpoint for critical in self.critical_endpoints):
                critical_endpoints_stats[endpoint] = self.get_endpoint_statistics(endpoint)

        return {
            'total_endpoints_monitored': len(self.endpoint_stats),
            'total_requests': total_requests,
            'overall_avg_response_time': sum(all_times) / len(all_times) if all_times else 0,
            'overall_success_rate': len([s for s in all_statuses if 200 <= s < 300]) / len(all_statuses) if all_statuses else 0,
            'slow_requests_total': len([t for t in all_times if t > self.slow_threshold]),
            'critical_endpoints': critical_endpoints_stats,
            'pool_current_stats': self._get_pool_stats()
        }

    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generar reporte completo de performance."""
        report = {
            'timestamp': time.time(),
            'monitoring_summary': self.get_endpoint_statistics(),
            'query_analyzer_stats': query_analyzer.get_query_statistics(),
            'pool_health': self._assess_pool_health(),
            'recommendations': self._generate_performance_recommendations()
        }

        return report

    def _assess_pool_health(self) -> Dict[str, Any]:
        """Evaluar salud del pool de conexiones."""
        stats = self._get_pool_stats()

        if 'error' in stats:
            return {'status': 'error', 'message': stats['error']}

        size = stats.get('size', 0)
        active = stats.get('active', 0)
        overflow = stats.get('overflow', 0)

        # Calcular utilización
        utilization = (active / size) if size > 0 else 0

        health_status = 'healthy'
        if utilization > 0.9:
            health_status = 'critical'
        elif utilization > 0.7:
            health_status = 'warning'

        return {
            'status': health_status,
            'utilization': utilization,
            'active_connections': active,
            'pool_size': size,
            'overflow_connections': overflow,
            'recommendations': self._get_pool_recommendations(utilization, overflow)
        }

    def _get_pool_recommendations(self, utilization: float, overflow: int) -> list:
        """Generar recomendaciones para el pool de conexiones."""
        recommendations = []

        if utilization > 0.9:
            recommendations.append('Pool utilization critical (>90%): consider increasing pool size')
        elif utilization > 0.7:
            recommendations.append('Pool utilization high (>70%): monitor for potential bottlenecks')

        if overflow > 0:
            recommendations.append(f'Pool overflow active ({overflow} connections): review connection management')

        if not recommendations:
            recommendations.append('Pool health is optimal')

        return recommendations

    def _generate_performance_recommendations(self) -> list:
        """Generar recomendaciones generales de performance."""
        recommendations = []

        # Analizar endpoints lentos
        slow_endpoints = []
        for endpoint, stats in self.endpoint_stats.items():
            if stats:
                avg_time = sum(s['process_time'] for s in stats) / len(stats)
                if avg_time > self.slow_threshold:
                    slow_endpoints.append((endpoint, avg_time))

        if slow_endpoints:
            recommendations.append(f'Found {len(slow_endpoints)} slow endpoints requiring optimization')
            for endpoint, avg_time in sorted(slow_endpoints, key=lambda x: x[1], reverse=True)[:3]:
                recommendations.append(f'Optimize {endpoint}: avg {avg_time:.3f}s')

        # Verificar pool health
        pool_health = self._assess_pool_health()
        if pool_health['status'] != 'healthy':
            recommendations.extend(pool_health.get('recommendations', []))

        if not recommendations:
            recommendations.append('System performance is optimal')

        return recommendations


# Instancia global del middleware
performance_monitor = None


def get_performance_monitor() -> PerformanceMonitorMiddleware:
    """Obtener instancia del monitor de performance."""
    global performance_monitor
    if performance_monitor is None:
        raise RuntimeError('Performance monitor not initialized')
    return performance_monitor


def init_performance_monitor(app, slow_threshold: float = 1.0) -> PerformanceMonitorMiddleware:
    """Inicializar y configurar el middleware de performance."""
    global performance_monitor
    performance_monitor = PerformanceMonitorMiddleware(app, slow_threshold)
    return performance_monitor
