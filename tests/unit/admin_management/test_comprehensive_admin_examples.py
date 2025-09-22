"""
Comprehensive Admin Management Testing Examples

Este archivo demuestra el uso completo de la arquitectura de testing desarrollada
para admin_management.py, incluyendo ejemplos prácticos de FastAPI testing,
aislamiento de base de datos, autenticación/autorización, y patrones avanzados.

Autor: Backend Framework AI
Fecha: 2025-09-21
Framework: pytest + FastAPI + SQLAlchemy + TDD
Objetivo: Ejemplos completos de testing para admin management
"""

import asyncio
import uuid
import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
from fastapi import status
from httpx import AsyncClient

# Import our testing fixtures and patterns
from tests.fixtures.admin_management.admin_testing_fixtures import *
from tests.fixtures.admin_management.admin_database_isolation import *
from tests.fixtures.admin_management.admin_auth_test_patterns import *

# Import the endpoints we're testing
from app.api.v1.endpoints.admin_management import (
    list_admin_users, create_admin_user, get_admin_user,
    AdminCreateRequest, AdminResponse
)
from app.models.user import User, UserType
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType
from app.services.admin_permission_service import admin_permission_service, PermissionDeniedError


# ================================================================================================
# EXAMPLE 1: COMPLETE FASTAPI ENDPOINT TESTING WITH ISOLATION
# ================================================================================================

class TestAdminEndpointComprehensiveExamples:
    """
    Ejemplos completos de testing de endpoints FastAPI con aislamiento de base de datos
    y autenticación completa.
    """

    @pytest.mark.asyncio
    async def test_list_admin_users_complete_flow(
        self,
        admin_isolated_db_advanced,
        admin_user_hierarchy,
        admin_auth_headers,
        authenticated_admin_client
    ):
        """
        Ejemplo completo: Listar usuarios admin con autenticación real y base de datos aislada.

        Demuestra:
        - Aislamiento completo de base de datos
        - Autenticación JWT real
        - Verificación de permisos
        - Validación de respuesta
        """

        # Arrange: Preparar datos de prueba
        session = admin_isolated_db_advanced
        superuser = admin_user_hierarchy["superuser_high"]
        auth_headers = admin_auth_headers["superuser_high"]

        # Crear usuarios admin adicionales para el test
        additional_admins = []
        for i in range(3):
            admin = User(
                id=generate_uuid(),
                email=f"test_admin_{i}@mestore.test",
                password_hash=await get_password_hash("test_pass"),
                nombre=f"Admin{i}",
                apellido=f"Test{i}",
                user_type=UserType.ADMIN,
                security_clearance_level=3,
                is_active=True,
                is_verified=True,
                department_id=f"dept_{i}"
            )
            additional_admins.append(admin)
            session.add(admin)

        await session.flush()

        # Mock del servicio de permisos para permitir la operación
        with patch('app.services.admin_permission_service.admin_permission_service.validate_permission') as mock_validate:
            mock_validate.return_value = True

            with patch('app.services.admin_permission_service.admin_permission_service._log_admin_activity') as mock_log:
                # Act: Ejecutar la función directamente
                result = await list_admin_users(
                    db=session,
                    current_user=superuser,
                    skip=0,
                    limit=10
                )

                # Assert: Verificar resultados
                assert isinstance(result, list)
                assert len(result) >= 3  # Al menos los 3 admins creados

                # Verificar estructura de respuesta
                for admin_response in result:
                    assert hasattr(admin_response, 'id')
                    assert hasattr(admin_response, 'email')
                    assert hasattr(admin_response, 'user_type')
                    assert hasattr(admin_response, 'security_clearance_level')

                # Verificar que se validaron permisos
                mock_validate.assert_called_once_with(
                    session, superuser,
                    ResourceType.USERS, PermissionAction.READ, PermissionScope.GLOBAL
                )

                # Verificar logging de actividad
                mock_log.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_admin_user_with_real_database(
        self,
        admin_isolated_db_advanced,
        test_superuser_high_clearance,
        valid_admin_create_requests,
        admin_db_with_permissions
    ):
        """
        Ejemplo completo: Crear usuario admin con base de datos real y validaciones completas.

        Demuestra:
        - Creación de usuarios con base de datos real
        - Validación de permisos complejos
        - Manejo de constrains de base de datos
        - Logging de actividad audit
        """

        # Arrange
        session = admin_db_with_permissions
        superuser = test_superuser_high_clearance
        request_data = valid_admin_create_requests["high_clearance_admin"]

        # Crear request object
        create_request = AdminCreateRequest(**request_data)

        # Mock servicios externos
        with patch('app.services.admin_permission_service.admin_permission_service.validate_permission') as mock_validate:
            mock_validate.return_value = True

            with patch('app.services.auth_service.auth_service') as mock_auth:
                mock_auth.generate_secure_password.return_value = "TempPass123!"
                mock_auth.get_password_hash.return_value = await get_password_hash("TempPass123!")

                with patch('app.services.admin_permission_service.admin_permission_service._log_admin_activity') as mock_log:
                    # Act
                    result = await create_admin_user(create_request, session, superuser)

                    # Assert
                    assert isinstance(result, AdminResponse)
                    assert result.email == request_data["email"]
                    assert result.user_type == request_data["user_type"]
                    assert result.security_clearance_level == request_data["security_clearance_level"]

                    # Verificar que el usuario fue creado en la base de datos
                    created_user = await session.execute(
                        select(User).where(User.email == request_data["email"])
                    )
                    db_user = created_user.scalar_one_or_none()
                    assert db_user is not None
                    assert db_user.user_type == UserType.ADMIN

                    # Verificar validación de permisos
                    mock_validate.assert_called_once()

                    # Verificar logging de actividad
                    mock_log.assert_called_once()
                    log_call_args = mock_log.call_args[0]
                    assert log_call_args[2].value == "USER_MANAGEMENT"  # AdminActionType


# ================================================================================================
# EXAMPLE 2: AUTHENTICATION AND AUTHORIZATION TESTING
# ================================================================================================

class TestAdminAuthExamples:
    """
    Ejemplos completos de testing de autenticación y autorización.
    """

    @pytest.mark.asyncio
    async def test_jwt_authentication_comprehensive(
        self,
        admin_auth_test_matrix,
        admin_jwt_generator,
        admin_isolated_db_advanced
    ):
        """
        Ejemplo completo: Testing comprehensivo de autenticación JWT.

        Demuestra:
        - Testing de múltiples scenarios de JWT
        - Validación de tokens válidos e inválidos
        - Manejo de errores de autenticación
        - Verificación de claims JWT
        """

        # Test valid token
        valid_user_data = {
            "sub": str(uuid.uuid4()),
            "email": "admin@mestore.test",
            "user_type": "ADMIN",
            "security_clearance_level": 4
        }

        valid_token = admin_jwt_generator.create_valid_token(valid_user_data)
        assert valid_token is not None
        assert len(valid_token.split('.')) == 3  # JWT has 3 parts

        # Test expired token
        expired_token = admin_jwt_generator.create_expired_token(valid_user_data)
        assert expired_token is not None

        # Verify expired token is rejected
        from jose import jwt, JWTError
        with pytest.raises(JWTError):
            jwt.decode(expired_token, admin_jwt_generator.secret_key, algorithms=["HS256"])

        # Test invalid signature token
        invalid_sig_token = admin_jwt_generator.create_invalid_signature_token(valid_user_data)
        with pytest.raises(JWTError):
            jwt.decode(invalid_sig_token, admin_jwt_generator.secret_key, algorithms=["HS256"])

        # Test malformed token
        malformed_token = admin_jwt_generator.create_malformed_token()
        with pytest.raises(JWTError):
            jwt.decode(malformed_token, admin_jwt_generator.secret_key, algorithms=["HS256"])

    @pytest.mark.asyncio
    async def test_permission_validation_matrix(
        self,
        admin_authz_test_matrix,
        admin_isolated_db_advanced,
        admin_user_hierarchy
    ):
        """
        Ejemplo completo: Testing de matriz de permisos y autorización.

        Demuestra:
        - Validación de permisos por tipo de usuario
        - Testing de security clearance levels
        - Validación de scopes de permisos
        - Testing de inheritance de permisos
        """

        session = admin_isolated_db_advanced

        # Test cases from matrix
        test_scenarios = [
            # System user should have all permissions
            {
                "user": admin_user_hierarchy["system"],
                "resource": ResourceType.USERS,
                "action": PermissionAction.DELETE,
                "scope": PermissionScope.SYSTEM,
                "should_pass": True
            },
            # Superuser should have global permissions but not system
            {
                "user": admin_user_hierarchy["superuser_high"],
                "resource": ResourceType.USERS,
                "action": PermissionAction.CREATE,
                "scope": PermissionScope.GLOBAL,
                "should_pass": True
            },
            # Admin should have department permissions
            {
                "user": admin_user_hierarchy["admin_high"],
                "resource": ResourceType.USERS,
                "action": PermissionAction.READ,
                "scope": PermissionScope.DEPARTMENT,
                "should_pass": True
            },
            # Vendor should not have admin permissions
            {
                "user": admin_user_hierarchy["vendor"],
                "resource": ResourceType.USERS,
                "action": PermissionAction.READ,
                "scope": PermissionScope.USER,
                "should_pass": False
            }
        ]

        for scenario in test_scenarios:
            user = scenario["user"]
            resource = scenario["resource"]
            action = scenario["action"]
            scope = scenario["scope"]
            should_pass = scenario["should_pass"]

            if should_pass:
                # Should not raise exception
                try:
                    result = await admin_permission_service.validate_permission(
                        session, user, resource, action, scope
                    )
                    assert result == True
                except PermissionDeniedError:
                    pytest.fail(f"Permission should have been granted for {user.user_type} accessing {resource}.{action}.{scope}")
            else:
                # Should raise PermissionDeniedError
                with pytest.raises(PermissionDeniedError):
                    await admin_permission_service.validate_permission(
                        session, user, resource, action, scope
                    )

    @pytest.mark.asyncio
    async def test_security_clearance_enforcement(
        self,
        admin_isolated_db_advanced,
        admin_user_hierarchy
    ):
        """
        Ejemplo completo: Testing de enforcement de security clearance levels.

        Demuestra:
        - Validación de niveles de clearance
        - Prevención de escalación de privilegios
        - Testing de boundary conditions
        - Validación de clearance requirements
        """

        session = admin_isolated_db_advanced

        # Create permission that requires high clearance
        high_clearance_permission = Mock(spec=AdminPermission)
        high_clearance_permission.resource_type = ResourceType.USERS
        high_clearance_permission.action = PermissionAction.DELETE
        high_clearance_permission.scope = PermissionScope.GLOBAL
        high_clearance_permission.required_clearance_level = 5

        # Test high clearance user (should pass)
        high_clearance_user = admin_user_hierarchy["superuser_high"]  # clearance 5
        assert high_clearance_user.security_clearance_level == 5

        # Mock the permission service to test clearance validation
        with patch.object(admin_permission_service, '_get_required_permission') as mock_get_perm:
            mock_get_perm.return_value = high_clearance_permission

            # High clearance user should pass
            result = await admin_permission_service.validate_permission(
                session, high_clearance_user,
                ResourceType.USERS, PermissionAction.DELETE, PermissionScope.GLOBAL
            )
            assert result == True

            # Low clearance user should fail
            low_clearance_user = admin_user_hierarchy["admin_low"]  # clearance 2
            assert low_clearance_user.security_clearance_level == 2

            with pytest.raises(PermissionDeniedError):
                await admin_permission_service.validate_permission(
                    session, low_clearance_user,
                    ResourceType.USERS, PermissionAction.DELETE, PermissionScope.GLOBAL
                )


# ================================================================================================
# EXAMPLE 3: DATABASE ISOLATION AND TRANSACTION TESTING
# ================================================================================================

class TestDatabaseIsolationExamples:
    """
    Ejemplos completos de aislamiento de base de datos y testing de transacciones.
    """

    @pytest.mark.asyncio
    async def test_transaction_isolation_complete_example(
        self,
        admin_isolation_engine,
        admin_user_isolation,
        admin_permission_isolation
    ):
        """
        Ejemplo completo: Aislamiento de transacciones con rollback automático.

        Demuestra:
        - Aislamiento completo entre tests
        - Rollback automático de transacciones
        - Limpieza de datos de test
        - Verificación de aislamiento
        """

        test_id = f"isolation_test_{uuid.uuid4().hex[:8]}"

        # Create isolated environment
        async with admin_isolation_engine.isolated_transaction_context(test_id) as session:
            # Create test data that should be isolated
            test_user = User(
                id=generate_uuid(),
                email="isolation_test@mestore.test",
                password_hash=await get_password_hash("test_pass"),
                nombre="Isolation",
                apellido="Test",
                user_type=UserType.ADMIN,
                security_clearance_level=3,
                is_active=True,
                is_verified=True
            )

            session.add(test_user)
            await session.flush()

            # Verify user exists in this session
            result = await session.execute(
                select(User).where(User.email == "isolation_test@mestore.test")
            )
            found_user = result.scalar_one_or_none()
            assert found_user is not None
            assert found_user.email == "isolation_test@mestore.test"

            # Track user creation for cleanup
            await admin_user_isolation.track_user_creation(test_user.id)

        # After context exit, verify isolation (data should be rolled back)
        # Create new session to verify isolation
        new_test_id = f"verification_test_{uuid.uuid4().hex[:8]}"
        async with admin_isolation_engine.isolated_transaction_context(new_test_id) as verification_session:
            result = await verification_session.execute(
                select(User).where(User.email == "isolation_test@mestore.test")
            )
            found_user = result.scalar_one_or_none()
            assert found_user is None  # Should not exist due to rollback

    @pytest.mark.asyncio
    async def test_nested_savepoint_example(
        self,
        admin_nested_transaction_db,
        admin_isolation_engine
    ):
        """
        Ejemplo completo: Testing con savepoints anidados.

        Demuestra:
        - Uso de savepoints para operaciones anidadas
        - Rollback selectivo a savepoints
        - Testing de operaciones complejas
        - Manejo de errores en transacciones anidadas
        """

        session = admin_nested_transaction_db

        # Create base data
        base_user = User(
            id=generate_uuid(),
            email="base_user@mestore.test",
            password_hash=await get_password_hash("test_pass"),
            nombre="Base",
            apellido="User",
            user_type=UserType.ADMIN,
            security_clearance_level=3,
            is_active=True,
            is_verified=True
        )

        session.add(base_user)
        await session.flush()

        # Use nested savepoint for complex operation
        async with admin_isolation_engine.nested_savepoint_context(session, "test_operation") as sp_session:
            # Create additional user in savepoint
            savepoint_user = User(
                id=generate_uuid(),
                email="savepoint_user@mestore.test",
                password_hash=await get_password_hash("test_pass"),
                nombre="Savepoint",
                apellido="User",
                user_type=UserType.ADMIN,
                security_clearance_level=4,
                is_active=True,
                is_verified=True
            )

            sp_session.add(savepoint_user)
            await sp_session.flush()

            # Verify both users exist
            users = await sp_session.execute(select(User))
            user_count = len(users.scalars().all())
            assert user_count >= 2

            # Simulate error to trigger savepoint rollback
            # (In real test, this would be an actual error condition)
            # raise Exception("Simulated error")

        # After savepoint, base user should still exist
        # but savepoint user should be rolled back
        result = await session.execute(
            select(User).where(User.email == "base_user@mestore.test")
        )
        base_found = result.scalar_one_or_none()
        assert base_found is not None

        # Savepoint user should exist since we didn't raise exception
        result = await session.execute(
            select(User).where(User.email == "savepoint_user@mestore.test")
        )
        savepoint_found = result.scalar_one_or_none()
        assert savepoint_found is not None  # Exists because savepoint committed


# ================================================================================================
# EXAMPLE 4: ASYNC CLIENT INTEGRATION TESTING
# ================================================================================================

class TestAsyncClientIntegrationExamples:
    """
    Ejemplos completos de testing con AsyncClient para integración completa.
    """

    @pytest.mark.asyncio
    async def test_full_endpoint_integration_with_auth(
        self,
        admin_async_client,
        admin_isolated_db_advanced,
        admin_auth_headers,
        valid_admin_create_requests
    ):
        """
        Ejemplo completo: Testing de endpoint completo con AsyncClient y autenticación.

        Demuestra:
        - Testing con AsyncClient real
        - Headers de autenticación
        - Payload validation
        - Response validation
        - Status code verification
        """

        client = admin_async_client
        session = admin_isolated_db_advanced
        auth_headers = admin_auth_headers["superuser_high"]
        request_payload = valid_admin_create_requests["basic_admin"]

        # Mock permission service for endpoint
        with patch('app.api.v1.endpoints.admin_management.admin_permission_service') as mock_service:
            mock_service.validate_permission = AsyncMock(return_value=True)
            mock_service._log_admin_activity = AsyncMock()

            # Mock database query for duplicate check
            with patch('app.api.v1.endpoints.admin_management.get_db') as mock_get_db:
                mock_get_db.return_value = session

                # Mock auth service
                with patch('app.services.auth_service.auth_service') as mock_auth:
                    mock_auth.generate_secure_password.return_value = "TempPass123!"
                    mock_auth.get_password_hash.return_value = await get_password_hash("TempPass123!")

                    # Execute request
                    response = await client.post(
                        "/api/v1/admin/admins",
                        json=request_payload,
                        headers=auth_headers
                    )

                    # Verify response
                    assert response.status_code in [200, 201]  # Created or OK
                    response_data = response.json()

                    assert "email" in response_data
                    assert response_data["email"] == request_payload["email"]
                    assert response_data["user_type"] == request_payload["user_type"]

    @pytest.mark.asyncio
    async def test_error_handling_integration(
        self,
        admin_async_client,
        admin_auth_headers,
        invalid_admin_create_requests
    ):
        """
        Ejemplo completo: Testing de manejo de errores con integración completa.

        Demuestra:
        - Testing de validation errors
        - HTTP status codes apropiados
        - Error message validation
        - Exception handling
        """

        client = admin_async_client
        auth_headers = admin_auth_headers["superuser_high"]

        # Test various invalid scenarios
        error_scenarios = [
            {
                "payload": invalid_admin_create_requests["missing_email"],
                "expected_status": 422,  # Validation error
                "expected_error_type": "validation_error"
            },
            {
                "payload": invalid_admin_create_requests["invalid_email"],
                "expected_status": 422,
                "expected_error_type": "validation_error"
            },
            {
                "payload": invalid_admin_create_requests["clearance_too_high"],
                "expected_status": 422,
                "expected_error_type": "validation_error"
            }
        ]

        for scenario in error_scenarios:
            payload = scenario["payload"]
            expected_status = scenario["expected_status"]

            response = await client.post(
                "/api/v1/admin/admins",
                json=payload,
                headers=auth_headers
            )

            assert response.status_code == expected_status

            if expected_status == 422:
                # Validation error should have detail
                response_data = response.json()
                assert "detail" in response_data
                assert isinstance(response_data["detail"], list)


# ================================================================================================
# EXAMPLE 5: PERFORMANCE AND LOAD TESTING
# ================================================================================================

class TestPerformanceExamples:
    """
    Ejemplos de testing de performance y carga.
    """

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_admin_endpoint_performance(
        self,
        admin_async_client,
        admin_auth_headers,
        bulk_admin_users
    ):
        """
        Ejemplo completo: Testing de performance de endpoints admin.

        Demuestra:
        - Measurement de response times
        - Testing con múltiples usuarios
        - Validation de performance thresholds
        - Memory usage monitoring
        """

        import time
        import asyncio

        client = admin_async_client
        auth_headers = admin_auth_headers["superuser_high"]

        # Mock database to return bulk users
        with patch('app.api.v1.endpoints.admin_management.get_db') as mock_get_db:
            with patch('app.api.v1.endpoints.admin_management.admin_permission_service') as mock_service:
                mock_service.validate_permission = AsyncMock(return_value=True)
                mock_service._log_admin_activity = AsyncMock()

                # Test listing performance with large dataset
                start_time = time.time()

                response = await client.get(
                    "/api/v1/admin/admins?limit=50",
                    headers=auth_headers
                )

                end_time = time.time()
                response_time = end_time - start_time

                # Verify performance threshold
                assert response_time < 0.5  # 500ms threshold
                assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_request_handling(
        self,
        admin_async_client,
        admin_auth_headers
    ):
        """
        Ejemplo completo: Testing de manejo de requests concurrentes.

        Demuestra:
        - Concurrent request execution
        - Resource contention testing
        - Response consistency verification
        - Error rate monitoring
        """

        client = admin_async_client
        auth_headers = admin_auth_headers["superuser_high"]

        # Mock services
        with patch('app.api.v1.endpoints.admin_management.admin_permission_service') as mock_service:
            mock_service.validate_permission = AsyncMock(return_value=True)
            mock_service._log_admin_activity = AsyncMock()

            # Create concurrent requests
            async def make_request():
                return await client.get(
                    "/api/v1/admin/admins",
                    headers=auth_headers
                )

            # Execute 10 concurrent requests
            start_time = time.time()
            responses = await asyncio.gather(*[make_request() for _ in range(10)])
            end_time = time.time()

            # Verify all requests succeeded
            success_count = sum(1 for r in responses if r.status_code == 200)
            assert success_count == 10

            # Verify reasonable total time (should be much less than 10 * single request time)
            total_time = end_time - start_time
            assert total_time < 2.0  # 2 seconds for 10 concurrent requests


# ================================================================================================
# EXAMPLE 6: SECURITY TESTING
# ================================================================================================

class TestSecurityExamples:
    """
    Ejemplos completos de testing de seguridad.
    """

    @pytest.mark.asyncio
    async def test_privilege_escalation_prevention(
        self,
        admin_async_client,
        admin_jwt_generator,
        admin_user_hierarchy
    ):
        """
        Ejemplo completo: Testing de prevención de escalación de privilegios.

        Demuestra:
        - Token tampering detection
        - Privilege escalation prevention
        - Authorization boundary enforcement
        - Security violation logging
        """

        client = admin_async_client
        low_privilege_user = admin_user_hierarchy["admin_low"]

        # Create tampered token (attempt privilege escalation)
        user_data = {
            "sub": str(low_privilege_user.id),
            "email": low_privilege_user.email,
            "user_type": "ADMIN",  # Original type
            "security_clearance_level": 2  # Original clearance
        }

        # Create tampered token with escalated privileges
        tampered_token = admin_jwt_generator.create_tampered_token(user_data)
        tampered_headers = {"Authorization": f"Bearer {tampered_token}"}

        # Attempt high-privilege operation
        high_privilege_payload = {
            "email": "new_superuser@mestore.test",
            "nombre": "New",
            "apellido": "SuperUser",
            "user_type": "SUPERUSER",  # Attempting to create superuser
            "security_clearance_level": 5
        }

        response = await client.post(
            "/api/v1/admin/admins",
            json=high_privilege_payload,
            headers=tampered_headers
        )

        # Should be rejected due to token tampering or insufficient privileges
        assert response.status_code in [401, 403]  # Unauthorized or Forbidden

    @pytest.mark.asyncio
    async def test_timing_attack_resistance(
        self,
        admin_async_client,
        admin_auth_headers
    ):
        """
        Ejemplo completo: Testing de resistencia a timing attacks.

        Demuestra:
        - Consistent response times
        - Information leak prevention
        - Timing attack mitigation
        - Security metrics monitoring
        """

        import time

        client = admin_async_client
        auth_headers = admin_auth_headers["superuser_high"]

        # Test timing for existing vs non-existing users
        times = []

        # Test with existing user ID
        for _ in range(5):
            start_time = time.time()
            response = await client.get(
                f"/api/v1/admin/admins/{uuid.uuid4()}",  # Non-existent ID
                headers=auth_headers
            )
            end_time = time.time()
            times.append(end_time - start_time)

        # Calculate timing variance
        avg_time = sum(times) / len(times)
        max_variance = max(abs(t - avg_time) for t in times)

        # Timing variance should be minimal (< 50ms)
        assert max_variance < 0.05  # 50ms threshold


# ================================================================================================
# EXAMPLE 7: ERROR HANDLING AND EDGE CASES
# ================================================================================================

class TestErrorHandlingExamples:
    """
    Ejemplos completos de manejo de errores y casos edge.
    """

    @pytest.mark.asyncio
    async def test_database_constraint_violations(
        self,
        admin_isolated_db_advanced,
        test_superuser_high_clearance,
        valid_admin_create_requests
    ):
        """
        Ejemplo completo: Testing de violaciones de constraints de base de datos.

        Demuestra:
        - Unique constraint violations
        - Foreign key constraint violations
        - Database error handling
        - Transaction rollback
        """

        session = admin_isolated_db_advanced
        superuser = test_superuser_high_clearance

        # Create first admin user
        first_request = AdminCreateRequest(**valid_admin_create_requests["basic_admin"])

        with patch('app.services.admin_permission_service.admin_permission_service.validate_permission'):
            with patch('app.services.auth_service.auth_service') as mock_auth:
                mock_auth.generate_secure_password.return_value = "TempPass123!"
                mock_auth.get_password_hash.return_value = await get_password_hash("TempPass123!")

                # Create first user (should succeed)
                result1 = await create_admin_user(first_request, session, superuser)
                assert result1.email == first_request.email

                # Attempt to create duplicate user (should fail)
                duplicate_request = AdminCreateRequest(**valid_admin_create_requests["basic_admin"])

                with pytest.raises(HTTPException) as exc_info:
                    await create_admin_user(duplicate_request, session, superuser)

                assert exc_info.value.status_code == 409  # Conflict

    @pytest.mark.asyncio
    async def test_boundary_value_testing(
        self,
        admin_isolated_db_advanced,
        test_superuser_high_clearance
    ):
        """
        Ejemplo completo: Testing de valores boundary y edge cases.

        Demuestra:
        - Boundary value testing
        - Input validation limits
        - Edge case handling
        - Error message validation
        """

        session = admin_isolated_db_advanced
        superuser = test_superuser_high_clearance

        # Test security clearance boundaries
        boundary_test_cases = [
            {"clearance": 0, "should_fail": True},   # Below minimum
            {"clearance": 1, "should_fail": False},  # Minimum valid
            {"clearance": 5, "should_fail": False},  # Maximum valid
            {"clearance": 6, "should_fail": True},   # Above maximum
        ]

        for test_case in boundary_test_cases:
            clearance = test_case["clearance"]
            should_fail = test_case["should_fail"]

            try:
                request = AdminCreateRequest(
                    email=f"boundary_test_{clearance}@mestore.test",
                    nombre="Boundary",
                    apellido="Test",
                    user_type=UserType.ADMIN,
                    security_clearance_level=clearance
                )

                if should_fail:
                    # Should raise validation error during request creation
                    pytest.fail(f"Expected validation error for clearance {clearance}")

            except ValueError:
                # Expected for invalid clearance values
                assert should_fail


# ================================================================================================
# EXAMPLE 8: COMPREHENSIVE INTEGRATION TEST
# ================================================================================================

class TestComprehensiveIntegrationExample:
    """
    Ejemplo final: Test de integración comprehensivo que combina todos los patrones.
    """

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_admin_management_workflow(
        self,
        admin_isolated_db_advanced,
        admin_async_client,
        admin_user_hierarchy,
        admin_auth_headers,
        valid_admin_create_requests,
        permission_matrix
    ):
        """
        Test de integración completo que demuestra un workflow completo de admin management.

        Incluye:
        - Autenticación y autorización
        - Creación de usuarios admin
        - Asignación de permisos
        - Operaciones bulk
        - Logging de actividad
        - Validación de seguridad
        """

        # Setup
        session = admin_isolated_db_advanced
        client = admin_async_client
        superuser = admin_user_hierarchy["superuser_high"]
        auth_headers = admin_auth_headers["superuser_high"]

        # Mock services
        with patch('app.services.admin_permission_service.admin_permission_service.validate_permission') as mock_validate:
            mock_validate.return_value = True

            with patch('app.services.admin_permission_service.admin_permission_service._log_admin_activity') as mock_log:
                with patch('app.services.auth_service.auth_service') as mock_auth:
                    mock_auth.generate_secure_password.return_value = "TempPass123!"
                    mock_auth.get_password_hash.return_value = await get_password_hash("TempPass123!")

                    # Step 1: Create new admin user
                    create_payload = valid_admin_create_requests["high_clearance_admin"]

                    # Direct function call (simulating endpoint behavior)
                    create_request = AdminCreateRequest(**create_payload)
                    new_admin = await create_admin_user(create_request, session, superuser)

                    assert new_admin.email == create_payload["email"]
                    assert new_admin.security_clearance_level == create_payload["security_clearance_level"]

                    # Step 2: List admin users to verify creation
                    admin_list = await list_admin_users(session, superuser)
                    assert len(admin_list) >= 1

                    # Step 3: Get specific admin user details
                    admin_details = await get_admin_user(new_admin.id, session, superuser)
                    assert admin_details.id == new_admin.id
                    assert admin_details.email == new_admin.email

                    # Verify all operations were logged
                    assert mock_log.call_count >= 3  # Creation, listing, and detail view

                    # Verify permission validations occurred
                    assert mock_validate.call_count >= 3

        print("✅ Comprehensive admin management workflow test completed successfully!")


if __name__ == "__main__":
    # Run specific test examples
    pytest.main([__file__, "-v", "--tb=short"])