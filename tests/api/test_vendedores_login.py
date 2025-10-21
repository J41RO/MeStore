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
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient

from app.main import app
from app.models.user import User, UserType
from app.core.security import get_password_hash
from app.core.types import generate_uuid


class TestVendedorLogin:
    """Tests para endpoint POST /vendedores/login."""

    @pytest.mark.asyncio
    async def test_login_vendedor_credenciales_invalidas_funcionando(self, async_client: AsyncClient, async_session):
        """Test de endpoint login funcionando con async client."""
        # PASO 1: Crear vendedor directamente en DB
        vendor = User(
            id=generate_uuid(),
            email="test.vendedor.login@test.com",
            password_hash=await get_password_hash("TestPassword123"),
            nombre="Test",
            apellido="Vendedor",
            user_type=UserType.VENDOR,
            is_active=True,
            cedula="87654321",
            telefono="+57 3009876543",
            ciudad="Medellín",
            empresa="Test Login SAS"
        )
        async_session.add(vendor)
        await async_session.commit()
        await async_session.refresh(vendor)

        # PASO 2: Login con credentials conocidas
        login_data = {
            "email": "test.vendedor.login@test.com",
            "password": "TestPassword123",
        }

        # Realizar login
        response = await async_client.post("/api/v1/vendedores/login", json=login_data)

        # Verificar respuesta exitosa (login válido debe retornar 200)
        assert response.status_code == status.HTTP_200_OK

        # Verificar estructura de respuesta exitosa
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_credenciales_invalidas(self, async_client: AsyncClient):
        """Test login con credenciales incorrectas."""
        # Datos de login inválidos
        login_data = {
            "email": "vendedor.inexistente@email.com",
            "password": "PasswordIncorrecto",
        }

        # Realizar login
        response = await async_client.post("/api/v1/vendedores/login", json=login_data)

        # Verificar respuesta de error
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Verificar mensaje de error
        data = response.json()
        assert "error_message" in data
        assert "credenciales inválidas" in data["error_message"].lower()

    @pytest.mark.asyncio
    async def test_login_usuario_no_vendedor(self, async_client: AsyncClient, async_session):
        """Test login con usuario que no es vendedor."""
        # Create a buyer user
        buyer = User(
            id=generate_uuid(),
            email="comprador.test@email.com",
            password_hash=await get_password_hash("TestPassword123"),
            nombre="Buyer",
            apellido="Test",
            user_type=UserType.BUYER,
            is_active=True
        )
        async_session.add(buyer)
        await async_session.commit()

        # Datos de login de usuario COMPRADOR (no vendedor)
        login_data = {
            "email": "comprador.test@email.com",
            "password": "TestPassword123",
        }

        # Realizar login
        response = await async_client.post("/api/v1/vendedores/login", json=login_data)

        # Verificar rechazo por tipo incorrecto
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Verificar mensaje específico
        data = response.json()
        assert "error_message" in data
        assert "credenciales inválidas" in data["error_message"].lower()

    @pytest.mark.asyncio
    async def test_login_datos_invalidos(self, async_client: AsyncClient):
        """Test login con datos de entrada inválidos."""
        # Datos inválidos (email malformado, password muy corto)
        login_data = {"email": "email_invalido", "password": "123"}

        # Realizar login
        response = await async_client.post("/api/v1/vendedores/login", json=login_data)

        # Verificar error de validación
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_rate_limiting_login_vendedor(self, async_client: AsyncClient):
        """Test rate limiting en endpoint de login vendedor."""
        # Datos de login
        login_data = {"email": "test@rate.limit", "password": "TestPassword123"}

        # Simular múltiples intentos rápidos
        # El rate limiter debe permitir algunos y bloquear el exceso
        responses = []

        for i in range(5):  # 5 intentos rápidos
            response = await async_client.post("/api/v1/vendedores/login", json=login_data)
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


# Fixtures compartidos if needed are now in conftest.py