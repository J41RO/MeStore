#!/usr/bin/env python3
"""
Integration Test Configuration with Enhanced Database Isolation
==============================================================

Configuración de pruebas de integración con aislamiento mejorado
para prevenir ResourceClosedError y garantizar coherencia entre
módulos.

Características:
1. Manejo asíncrono de sesiones
2. Inyección de dependencias FastAPI limpia
3. Creación automática de usuarios de prueba (superuser, vendor, buyer)
4. Generación de tokens JWT válidos
5. Limpieza y aislamiento entre tests
"""

import os
import asyncio
import logging
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# ==========================================================
# 🔧 Configuración del entorno de pruebas
# ==========================================================

# IMPORTANT: Set up temporary database path BEFORE any app imports
import tempfile
temp_db = tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False)
temp_db_path = temp_db.name
temp_db.close()

os.environ["TESTING"] = "1"
os.environ["DISABLE_SEARCH_SERVICE"] = "1"
os.environ["DISABLE_CHROMA_SERVICE"] = "1"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{temp_db_path}"

# Store temp db path for cleanup
_TEMP_DB_PATH = temp_db_path

from app.main import app
from app.models.user import User, UserType
from app.core.security import create_access_token, get_password_hash
from app.core.types import generate_uuid

# Enhanced database isolation tools
from tests.integration.database_isolation_enhanced import enhanced_async_session, session_manager

# ==========================================================
# 🧩 Fixtures base de sesión y cliente
# ==========================================================

@pytest.fixture(scope="function")
async def db_session(enhanced_async_session: AsyncSession) -> AsyncSession:
    """Alias de compatibilidad para pruebas heredadas."""
    if not hasattr(enhanced_async_session, "query"):
        def _unsupported_query(*_args, **_kwargs):  # pragma: no cover
            raise AttributeError("AsyncSession no soporta .query; usa SQLAlchemy select()")
        setattr(enhanced_async_session, "query", _unsupported_query)
    return enhanced_async_session


@pytest.fixture(scope="function")
async def integration_async_client(
    enhanced_async_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """
    Cliente HTTP asíncrono para pruebas de integración.

    - Usa sesión de base de datos aislada
    - Configura headers realistas
    - Limpia conexiones al finalizar
    """
    headers = {
        "User-Agent": "Integration-Test/1.0",
        "Content-Type": "application/json"
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers=headers,
        timeout=30.0
    ) as client:
        yield client

# ==========================================================
# 👥 Fixtures de usuarios de integración
# ==========================================================

async def _create_user(
    session: AsyncSession,
    email_prefix: str,
    password: str,
    user_type: UserType,
    nombre: str,
    apellido: str,
    telefono: str
) -> User:
    """Crea un usuario genérico para integración."""
    suffix = generate_uuid()[:8]
    user = User(
        id=generate_uuid(),
        email=f"integration.{email_prefix}+{suffix}@mestore.com",
        password_hash=await get_password_hash(password),
        nombre=nombre,
        apellido=apellido,
        user_type=user_type,
        is_active=True,
        is_verified=True,
        documento=generate_uuid()[:10],
        telefono=telefono
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def integration_superuser(enhanced_async_session: AsyncSession) -> User:
    """Superusuario de integración."""
    return await _create_user(
        enhanced_async_session,
        "superuser",
        "SuperSecure123!",
        UserType.SUPERUSER,
        "Integration",
        "Superuser",
        "3001234567"
    )


@pytest.fixture(scope="function")
async def integration_vendor(enhanced_async_session: AsyncSession) -> User:
    """Vendedor de integración."""
    return await _create_user(
        enhanced_async_session,
        "vendor",
        "VendorSecure123!",
        UserType.VENDOR,
        "Integration",
        "Vendor",
        "3009876543"
    )


@pytest.fixture(scope="function")
async def integration_buyer(enhanced_async_session: AsyncSession) -> User:
    """Comprador de integración."""
    return await _create_user(
        enhanced_async_session,
        "buyer",
        "BuyerSecure123!",
        UserType.BUYER,
        "Integration",
        "Buyer",
        "3005566778"
    )

# ==========================================================
# 🔐 Fixtures de tokens y cabeceras
# ==========================================================

def _make_token(user: User) -> str:
    """Genera un JWT válido para un usuario dado."""
    token_data = {
        "sub": str(user.id),
        "user_id": str(user.id),
        "email": user.email,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "user_type": user.user_type.value,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "documento": user.documento,
        "telefono": user.telefono,
    }
    return create_access_token(data=token_data)


@pytest.fixture(scope="function")
def integration_superuser_token(integration_superuser: User) -> str:
    return _make_token(integration_superuser)


@pytest.fixture(scope="function")
def integration_vendor_token(integration_vendor: User) -> str:
    return _make_token(integration_vendor)


@pytest.fixture(scope="function")
def integration_buyer_token(integration_buyer: User) -> str:
    return _make_token(integration_buyer)


def _auth_headers(token: str) -> dict:
    """Crea headers con token JWT."""
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture(scope="function")
def integration_superuser_headers(integration_superuser_token: str) -> dict:
    return _auth_headers(integration_superuser_token)


@pytest.fixture(scope="function")
def integration_vendor_headers(integration_vendor_token: str) -> dict:
    return _auth_headers(integration_vendor_token)


@pytest.fixture(scope="function")
def integration_buyer_headers(integration_buyer_token: str) -> dict:
    return _auth_headers(integration_buyer_token)

# ==========================================================
# 🧹 Limpieza automática tras cada test
# ==========================================================

@pytest.fixture(scope="function", autouse=True)
async def cleanup_integration_test():
    """
    Limpieza post-test para prevenir ResourceClosedError
    y mantener aislamiento de sesiones.
    """
    yield
    try:
        await session_manager.cleanup_all_sessions()
        session_manager.clear_dependency_overrides()
    except Exception as e:
        logging.getLogger(__name__).warning(f"⚠️ Limpieza de test falló: {e}")

# ==========================================================
# 🧭 Aliases de compatibilidad (legacy)
# ==========================================================
async_session = enhanced_async_session
async_client = integration_async_client
test_admin_user = integration_superuser
test_vendor_user = integration_vendor
test_buyer_user = integration_buyer
test_buyer = integration_buyer

# ==========================================================
# 🧹 Limpieza final de sesión completa
# ==========================================================

def pytest_sessionfinish(session, exitstatus):
    """Limpieza al finalizar toda la sesión de pytest"""
    try:
        import os
        if os.path.exists(_TEMP_DB_PATH):
            os.unlink(_TEMP_DB_PATH)
            logging.getLogger(__name__).info(f"Removed temporary database: {_TEMP_DB_PATH}")
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to remove temporary database: {e}")
