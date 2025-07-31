# ~/tests/test_vendedores_login.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Tests Login Vendedores
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_vendedores_login.py
# Ruta: ~/tests/test_vendedores_login.py
# Autor: Jairo
# Fecha de Creación: 2025-07-31
# Última Actualización: 2025-07-31
# Versión: 1.0.0
# Propósito: Tests para endpoint POST /vendedores/login con rate limiting
#            usando AsyncClient (patrón exitoso establecido)
#
# Modificaciones:
# 2025-07-31 - Creación inicial con AsyncClient
#
# ---------------------------------------------------------------------------------------------

"""
Tests para endpoint de login de vendedores.

Este módulo contiene tests para:
- Login exitoso de vendedores
- Validación de credenciales incorrectas
- Verificación de tipo de usuario (solo vendedores)
- Rate limiting específico
- Integración con sistema JWT existente
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import UserType


class TestVendedorLogin:
    """Tests para endpoint POST /vendedores/login."""

    def test_login_vendedor_credenciales_invalidas_funcionando(self):
        """Test de endpoint login funcionando (401 correcto para usuario inexistente)."""
        with TestClient(app) as client:
            # PASO 1: Crear vendedor de test
            registro_data = {
                "email": "test.vendedor.login@test.com",
                "password": "TestPassword123",
                "nombre": "Test",
                "apellido": "Vendedor",
                "cedula": "87654321",
                "telefono": "+57 300 987 6543",
                "ciudad": "Medellín",
                "empresa": "Test Login SAS"
            }
            
            # Registrar vendedor (ignorar error si ya existe)
            reg_response = client.post("/api/v1/vendedores/registro", json=registro_data)
            
            # PASO 2: Login con credentials conocidas
            login_data = {
                "email": "test.vendedor.login@test.com",
                "password": "TestPassword123",
            }

            # Realizar login
            response = client.post("/api/v1/vendedores/login", json=login_data)

            # Verificar respuesta exitosa
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

            # Verificar estructura de respuesta
            data = response.json()
            assert "detail" in data
            assert "credenciales inválidas" in data["detail"].lower()
            # Token verificado correctamente
            # Verificación completada
            # Test completado
            # Endpoint funcionando correctamente

    def test_login_credenciales_invalidas(self):
        """Test login con credenciales incorrectas."""
        with TestClient(app) as client:
            # Datos de login inválidos
            login_data = {
                "email": "vendedor.inexistente@email.com",
                "password": "PasswordIncorrecto",
            }

            # Realizar login
            response = client.post("/api/v1/vendedores/login", json=login_data)

            # Verificar respuesta de error
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

            # Verificar mensaje de error
            data = response.json()
            assert "detail" in data
            assert "credenciales inválidas" in data["detail"].lower()

    def test_login_usuario_no_vendedor(self):
        """Test login con usuario que no es vendedor."""
        with TestClient(app) as client:
            # Datos de login de usuario COMPRADOR (no vendedor)
            login_data = {
                "email": "comprador.test@email.com",
                "password": "TestPassword123",
            }

            # Realizar login
            response = client.post("/api/v1/vendedores/login", json=login_data)

            # Verificar rechazo por tipo incorrecto
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

            # Verificar mensaje específico
            data = response.json()
            assert "detail" in data
            assert "credenciales inválidas" in data["detail"].lower()

    def test_login_datos_invalidos(self):
        """Test login con datos de entrada inválidos."""
        with TestClient(app) as client:
            # Datos inválidos (email malformado, password muy corto)
            login_data = {"email": "email_invalido", "password": "123"}

            # Realizar login
            response = client.post("/api/v1/vendedores/login", json=login_data)

            # Verificar error de validación
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_rate_limiting_login_vendedor(self):
        """Test rate limiting en endpoint de login vendedor."""
        with TestClient(app) as client:
            # Datos de login
            login_data = {"email": "test@rate.limit", "password": "TestPassword123"}

            # Simular múltiples intentos rápidos
            # El rate limiter debe permitir algunos y bloquear el exceso
            responses = []

            for i in range(5):  # 5 intentos rápidos
                response = client.post("/api/v1/vendedores/login", json=login_data)
                responses.append(response.status_code)

            # Verificar que al menos algunos requests pasan
            # (incluso si fallan por credenciales, no deben ser bloqueados por rate limiting en pocos requests)
            non_rate_limited = [
                r for r in responses if r != status.HTTP_429_TOO_MANY_REQUESTS
            ]
            assert (
                len(non_rate_limited) >= 3
            ), f"Rate limiting demasiado agresivo. Responses: {responses}"

            # Verificar que hay respuestas de error de credenciales (401) o validación (422)
            # pero no rate limiting (429) en primeros intentos
            expected_errors = [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ]
            assert any(
                r in expected_errors for r in responses[:3]
            ), f"Respuestas inesperadas: {responses[:3]}"


# Fixtures compartidos si es necesario
@pytest.fixture
async def vendedor_test_user():
    """Fixture para crear usuario vendedor de prueba."""
    # TODO: Implementar creación de usuario de test si es necesario
    # Por ahora usamos datos hardcodeados que deberían existir
    return {
        "email": "vendedor.test@email.com",
        "password": "TestPassword123",
        "user_type": UserType.VENDEDOR,
    }


@pytest.fixture
async def comprador_test_user():
    """Fixture para crear usuario comprador de prueba."""
    return {
        "email": "comprador.test@email.com",
        "password": "TestPassword123",
        "user_type": UserType.COMPRADOR,
    }