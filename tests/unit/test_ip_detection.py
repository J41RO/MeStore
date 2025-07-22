# ~/tests/unit/test_ip_detection.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Tests Unitarios para Middleware de Detección de IPs Sospechosas
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_ip_detection.py
# Ruta: ~/tests/unit/test_ip_detection.py
# Autor: Jairo
# Fecha de Creación: 2025-07-22
# Última Actualización: 2025-07-22
# Versión: 1.0.0
# Propósito: Tests unitarios completos para el middleware de detección de IPs sospechosas,
#            cubriendo casos de bloqueo, logging y comportamiento del middleware
#
# Modificaciones:
# 2025-07-22 - Implementación inicial de tests unitarios para SuspiciousIPMiddleware
#
# ---------------------------------------------------------------------------------------------

"""
Tests unitarios para SuspiciousIPMiddleware.

Cubre:
- Bloqueo de IPs en lista negra
- Detección de User-Agents sospechosos
- Logging de eventos de seguridad
- Rutas excluidas de verificación
- Configuración dinámica del middleware
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.middleware.ip_detection import SuspiciousIPMiddleware


class TestSuspiciousIPMiddleware:
    """Test suite para SuspiciousIPMiddleware."""

    def setup_method(self):
        """Setup para cada test."""
        self.app = FastAPI()
        self.suspicious_ips = ['192.168.1.100', '10.0.0.5', '127.0.0.1']
        self.middleware = SuspiciousIPMiddleware(
            app=self.app,
            suspicious_ips=self.suspicious_ips,
            enable_blacklist=True
        )

    @pytest.mark.asyncio
    async def test_middleware_initialization(self):
        """Test inicialización correcta del middleware."""
        # Verificar que las IPs sospechosas se cargaron
        assert '192.168.1.100' in self.middleware.suspicious_ips
        assert '10.0.0.5' in self.middleware.suspicious_ips
        assert '127.0.0.1' in self.middleware.suspicious_ips

        # Verificar configuración
        assert self.middleware.enable_blacklist is True
        assert '/health' in self.middleware.excluded_paths
        assert '/docs' in self.middleware.excluded_paths

    @pytest.mark.asyncio
    async def test_suspicious_ip_blocked(self):
        """Test que IP sospechosa es bloqueada."""
        # Mock request con IP sospechosa
        request = self._create_mock_request(
            client_ip='192.168.1.100',
            user_agent='Mozilla/5.0',
            path='/api/users',
            method='GET'
        )

        # Mock call_next
        call_next = AsyncMock()

        with patch('app.core.middleware.ip_detection.logger') as mock_logger:
            # Ejecutar middleware
            response = await self.middleware.dispatch(request, call_next)

            # Verificar que se bloqueó
            assert response.status_code == 403
            assert 'Access denied' in str(response.body)

            # Verificar que se loggeó
            mock_logger.warning.assert_called_once()
            log_call = mock_logger.warning.call_args
            assert 'SECURITY ALERT: Suspicious IP detected' in log_call[0][0]
            assert log_call[1]['client_ip'] == '192.168.1.100'
            assert log_call[1]['action'] == 'blocked'
            assert log_call[1]['reason'] == 'ip_blacklist'

            # Verificar que call_next NO se llamó
            call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_allowed_ip_passes(self):
        """Test que IP permitida pasa sin problemas."""
        # Mock request con IP permitida
        request = self._create_mock_request(
            client_ip='192.0.2.1',    # IP de documentación RFC (TEST-NET-1) no en lista
            user_agent='Mozilla/5.0',
            path='/api/users',
            method='GET'
        )

        # Mock call_next y response
        mock_response = MagicMock()
        mock_response.status_code = 200
        call_next = AsyncMock(return_value=mock_response)

        with patch('app.core.middleware.ip_detection.logger'):
            # Ejecutar middleware
            response = await self.middleware.dispatch(request, call_next)

            # Verificar que pasó
            assert response == mock_response

            # Verificar que call_next se llamó
            call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_excluded_paths_bypass_check(self):
        """Test que rutas excluidas omiten verificación."""
        # Mock request a ruta excluida con IP sospechosa
        request = self._create_mock_request(
            client_ip='192.168.1.100',  # IP sospechosa
            user_agent='curl/7.68.0',   # User-Agent sospechoso
            path='/health',             # Ruta excluida
            method='GET'
        )

        # Mock call_next
        mock_response = MagicMock()
        call_next = AsyncMock(return_value=mock_response)

        with patch('app.core.middleware.ip_detection.logger') as mock_logger:
            # Ejecutar middleware
            response = await self.middleware.dispatch(request, call_next)

            # Verificar que pasó sin bloqueo
            assert response == mock_response
            call_next.assert_called_once_with(request)

            # Verificar que NO se loggeó warning
            mock_logger.warning.assert_not_called()

    @pytest.mark.asyncio
    async def test_suspicious_user_agent_flagged(self):
        """Test que User-Agent sospechoso se loggea pero permite acceso."""
        # Mock request con User-Agent sospechoso pero IP permitida
        request = self._create_mock_request(
            client_ip='192.0.2.1',       # IP de documentación RFC permitida
            user_agent='python-requests/2.28.0',  # User-Agent sospechoso
            path='/api/users',
            method='GET'
        )

        # Mock call_next
        mock_response = MagicMock()
        call_next = AsyncMock(return_value=mock_response)

        with patch('app.core.middleware.ip_detection.logger') as mock_logger:
            # Ejecutar middleware
            response = await self.middleware.dispatch(request, call_next)

            # Verificar que pasó (no se bloqueó)
            assert response == mock_response
            call_next.assert_called_once_with(request)

            # Verificar que se loggeó warning
            mock_logger.warning.assert_called_once()
            log_call = mock_logger.warning.call_args
            assert 'SECURITY ALERT: Suspicious User-Agent detected' in log_call[0][0]
            assert log_call[1]['action'] == 'flagged'
            assert log_call[1]['reason'] == 'suspicious_user_agent'

    @pytest.mark.asyncio
    async def test_empty_user_agent_flagged(self):
        """Test que User-Agent vacío se considera sospechoso."""
        request = self._create_mock_request(
            client_ip='192.0.2.1',    # IP de documentación RFC (no en blacklist)
            user_agent='',  # User-Agent vacío
            path='/api/users',
            method='GET'
        )

        mock_response = MagicMock()
        call_next = AsyncMock(return_value=mock_response)

        with patch('app.core.middleware.ip_detection.logger') as mock_logger:
            response = await self.middleware.dispatch(request, call_next)

            # Verificar que pasó pero se loggeó
            assert response == mock_response
            mock_logger.warning.assert_called_once()
            log_call = mock_logger.warning.call_args
            assert 'suspicious_user_agent' in log_call[1]['reason']

    @pytest.mark.asyncio
    async def test_x_forwarded_for_header(self):
        """Test que se usa X-Forwarded-For cuando está disponible."""
        # Mock request con X-Forwarded-For
        request = self._create_mock_request(
            client_ip='10.0.0.1',  # IP directa
            user_agent='Mozilla/5.0',
            path='/api/users',
            method='GET'
        )
        # Agregar header X-Forwarded-For con IP sospechosa
        request.headers = {'x-forwarded-for': '192.168.1.100, 10.0.0.1'}

        call_next = AsyncMock()

        with patch('app.core.middleware.ip_detection.logger') as mock_logger:
            response = await self.middleware.dispatch(request, call_next)

            # Verificar que se bloqueó usando la IP del X-Forwarded-For
            assert response.status_code == 403
            mock_logger.warning.assert_called_once()
            log_call = mock_logger.warning.call_args
            assert log_call[1]['client_ip'] == '192.168.1.100'

    @pytest.mark.asyncio
    async def test_middleware_with_blacklist_disabled(self):
        """Test middleware con blacklist deshabilitada."""
        # Crear middleware con blacklist deshabilitada
        middleware_disabled = SuspiciousIPMiddleware(
            app=self.app,
            suspicious_ips=['192.168.1.100'],
            enable_blacklist=False
        )

        # Request con IP sospechosa
        request = self._create_mock_request(
            client_ip='192.168.1.100',
            user_agent='Mozilla/5.0',
            path='/api/users',
            method='GET'
        )

        mock_response = MagicMock()
        call_next = AsyncMock(return_value=mock_response)

        with patch('app.core.middleware.ip_detection.logger') as mock_logger:
            response = await middleware_disabled.dispatch(request, call_next)

            # Verificar que NO se bloqueó
            assert response == mock_response
            call_next.assert_called_once_with(request)

            # Verificar que NO se loggeó por IP (blacklist deshabilitada)
            # Pero sí se puede loggear por otros motivos si aplica

    @pytest.mark.asyncio
    async def test_add_remove_suspicious_ip(self):
        """Test agregar y remover IPs sospechosas dinámicamente."""
        new_ip = '203.0.113.100'

        # Verificar que IP no está inicialmente
        assert new_ip not in self.middleware.suspicious_ips

        # Agregar IP
        with patch('app.core.middleware.ip_detection.logger') as mock_logger:
            self.middleware.add_suspicious_ip(new_ip)

            # Verificar que se agregó
            assert new_ip in self.middleware.suspicious_ips
            mock_logger.info.assert_called_with(f'IP agregada a lista negra: {new_ip}')

        # Remover IP
        with patch('app.core.middleware.ip_detection.logger') as mock_logger:
            self.middleware.remove_suspicious_ip(new_ip)

            # Verificar que se removió
            assert new_ip not in self.middleware.suspicious_ips
            mock_logger.info.assert_called_with(f'IP removida de lista negra: {new_ip}')

    def test_get_stats(self):
        """Test obtener estadísticas del middleware."""
        stats = self.middleware.get_stats()

        # Verificar estructura de estadísticas
        assert 'suspicious_ips_count' in stats
        assert 'blacklist_enabled' in stats
        assert 'excluded_paths' in stats
        assert 'suspicious_user_agents' in stats

        # Verificar valores
        assert stats['suspicious_ips_count'] >= 3  # Al menos las que agregamos
        assert stats['blacklist_enabled'] is True
        assert '/health' in stats['excluded_paths']

    def _create_mock_request(self, client_ip: str, user_agent: str, path: str, method: str) -> Request:
        """Crear mock request para testing."""
        request = MagicMock(spec=Request)
        request.url.path = path
        request.method = method
        request.headers = {'user-agent': user_agent}
        request.client.host = client_ip

        return request


@pytest.mark.asyncio
async def test_middleware_integration():
    """Test de integración básica del middleware."""
    # Crear app FastAPI con middleware
    app = FastAPI()

    # Agregar middleware
    app.add_middleware(
        SuspiciousIPMiddleware,
        suspicious_ips=['192.168.1.100'],
        enable_blacklist=True
    )

    # Agregar endpoint de prueba
    @app.get('/test')
    async def test_endpoint():
        return {'message': 'success'}

    # Crear client de prueba
    client = TestClient(app)

    # Test con IP permitida
    with patch('app.core.middleware.ip_detection.logger'):
        response = client.get('/test', headers={'user-agent': 'Mozilla/5.0'})
        assert response.status_code == 200
        assert response.json() == {'message': 'success'}

    # Test con IP sospechosa (simulada con headers)
    with patch('app.core.middleware.ip_detection.logger'):
        response = client.get(
            '/test',
            headers={
                'user-agent': 'Mozilla/5.0',
                'x-forwarded-for': '192.168.1.100'
            }
        )
        assert response.status_code == 403
        assert 'Access denied' in response.json()['detail']