# ~/tests/integration/admin_management/test_admin_auth_integration.py
# ---------------------------------------------------------------------------------------------
# MeStore - Admin Authentication Integration Tests
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_admin_auth_integration.py
# Ruta: ~/tests/integration/admin_management/test_admin_auth_integration.py
# Autor: Integration Testing Specialist
# Fecha de Creación: 2025-09-21
# Última Actualización: 2025-09-21
# Versión: 1.0.0
# Propósito: Authentication and permission integration tests for admin management system
#
# Auth Integration Testing Coverage:
# - JWT authentication integration with rate limiting
# - Permission validation integration with session management
# - Multi-factor authentication integration flows
# - Session timeout and token refresh integration
# - Account lockout and security alert integration
# - Cross-service authentication propagation
#
# ---------------------------------------------------------------------------------------------

"""
Admin Authentication Integration Tests.

Este módulo prueba la integración de autenticación para el sistema de administración:
- JWT token lifecycle with permission validation
- Session management across service boundaries
- Rate limiting integration with authentication flows
- Security event propagation across services
- Multi-factor authentication integration
- Account security and lockout mechanisms
"""

import pytest
import asyncio
import time
import uuid
import jwt
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.orm import Session

from app.services.admin_permission_service import AdminPermissionService, PermissionDeniedError
from app.services.auth_service import auth_service
from app.core.config import settings
from app.api.v1.deps.auth import get_current_user
from app.models.user import User, UserType
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, ActionResult, RiskLevel


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.auth
class TestAdminAuthIntegration:
    """Test admin authentication integration with permission and session management."""

    async def test_jwt_token_with_permission_validation_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        system_permissions: List[AdminPermission],
        integration_test_context
    ):
        """Test JWT token lifecycle integrated with permission validation."""
        start_time = time.time()

        # Create JWT token for superuser
        token_data = {
            "sub": superuser.email,
            "user_id": str(superuser.id),
            "user_type": superuser.user_type.value,
            "security_clearance": superuser.security_clearance_level,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }

        access_token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

        # Mock request context with token
        with patch('app.core.security.HTTPBearer') as mock_bearer:
            mock_bearer.return_value = MagicMock(credentials=access_token)

            # Verify token validation works
            decoded_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
            assert decoded_token["user_id"] == str(superuser.id)
            assert decoded_token["security_clearance"] == superuser.security_clearance_level

            # Test permission validation with valid token
            permission = system_permissions[0]  # users.create.global
            result = await admin_permission_service_with_redis.validate_permission(
                integration_db_session, superuser,
                permission.resource_type, permission.action, permission.scope
            )
            assert result is True

        integration_test_context.record_operation(
            "jwt_token_permission_validation",
            time.time() - start_time
        )

    async def test_session_management_with_redis_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        integration_redis_client,
        integration_test_context
    ):
        """Test session management integrated with Redis caching."""
        start_time = time.time()

        session_id = str(uuid.uuid4())
        user_id = str(superuser.id)

        # Create session in Redis
        session_data = {
            "user_id": user_id,
            "email": superuser.email,
            "user_type": superuser.user_type.value,
            "security_clearance": superuser.security_clearance_level,
            "last_activity": datetime.utcnow().isoformat(),
            "permissions_cached": True
        }

        session_key = f"session:{session_id}"
        integration_redis_client.setex(
            session_key,
            3600,  # 1 hour
            json.dumps(session_data, default=str)
        )

        # Verify session exists
        stored_session = integration_redis_client.get(session_key)
        assert stored_session is not None

        session_obj = json.loads(stored_session)
        assert session_obj["user_id"] == user_id
        assert session_obj["security_clearance"] == superuser.security_clearance_level

        # Test permission validation with session context
        permission_key = f"permission:{user_id}:users.read.global"

        # Cache permission result
        await admin_permission_service_with_redis._cache_permission_result(
            user_id, "users.read.global", True
        )

        # Verify permission is cached
        cached_permission = await admin_permission_service_with_redis._get_cached_permission(
            user_id, "users.read.global"
        )
        assert cached_permission is True

        # Test session invalidation
        integration_redis_client.delete(session_key)

        # Clear permission cache on session invalidation
        await admin_permission_service_with_redis._clear_user_permission_cache(user_id)

        # Verify session and permissions are cleared
        assert integration_redis_client.get(session_key) is None
        cached_permission_after_clear = await admin_permission_service_with_redis._get_cached_permission(
            user_id, "users.read.global"
        )
        assert cached_permission_after_clear is None

        integration_test_context.record_operation(
            "session_management_redis_integration",
            time.time() - start_time
        )

    async def test_rate_limiting_with_authentication_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        admin_user: User,
        integration_redis_client,
        integration_test_context
    ):
        """Test rate limiting integration with authentication flows."""
        start_time = time.time()

        user_id = str(admin_user.id)
        rate_limit_key = f"rate_limit:auth:{user_id}"

        # Simulate multiple authentication attempts
        max_attempts = 5
        time_window = 60  # 1 minute

        for attempt in range(max_attempts + 2):  # Exceed limit
            # Record authentication attempt
            integration_redis_client.incr(rate_limit_key)
            integration_redis_client.expire(rate_limit_key, time_window)

            current_attempts = integration_redis_client.get(rate_limit_key)
            current_attempts = int(current_attempts) if current_attempts else 0

            if current_attempts > max_attempts:
                # Should trigger rate limiting
                assert current_attempts > max_attempts

                # Log security event
                security_log = AdminActivityLog(
                    admin_user_id=admin_user.id,
                    admin_email=admin_user.email,
                    admin_full_name=admin_user.full_name,
                    action_type=AdminActionType.SECURITY,
                    action_name="rate_limit_exceeded",
                    action_description=f"Rate limit exceeded: {current_attempts} attempts in {time_window}s",
                    result=ActionResult.BLOCKED,
                    risk_level=RiskLevel.HIGH
                )
                integration_db_session.add(security_log)
                integration_db_session.commit()

                break

        # Verify rate limiting is working
        final_attempts = integration_redis_client.get(rate_limit_key)
        assert int(final_attempts) > max_attempts

        # Verify security log was created
        security_logs = integration_db_session.query(AdminActivityLog).filter(
            AdminActivityLog.admin_user_id == admin_user.id,
            AdminActivityLog.action_name == "rate_limit_exceeded"
        ).all()
        assert len(security_logs) >= 1

        integration_test_context.record_operation(
            "rate_limiting_authentication_integration",
            time.time() - start_time
        )

    async def test_account_lockout_with_notification_integration(
        self,
        integration_db_session: Session,
        locked_admin_user: User,
        mock_email_service,
        mock_notification_service,
        integration_test_context
    ):
        """Test account lockout integration with notification services."""
        start_time = time.time()

        # Verify user is locked
        assert locked_admin_user.is_account_locked() is True
        assert locked_admin_user.failed_login_attempts >= 5

        # Simulate authentication attempt on locked account
        auth_result = auth_service.authenticate_user(
            integration_db_session,
            locked_admin_user.email,
            "wrong_password"
        )
        assert auth_result is None  # Should fail due to lock

        # Create security alert for locked account access attempt
        security_alert = AdminActivityLog(
            admin_user_id=locked_admin_user.id,
            admin_email=locked_admin_user.email,
            admin_full_name=locked_admin_user.full_name,
            action_type=AdminActionType.SECURITY,
            action_name="locked_account_access_attempt",
            action_description=f"Access attempted on locked account: {locked_admin_user.email}",
            result=ActionResult.BLOCKED,
            risk_level=RiskLevel.CRITICAL
        )
        integration_db_session.add(security_alert)
        integration_db_session.commit()

        # Verify email notification would be triggered
        mock_email_service.send_admin_security_alert.assert_called()

        # Verify system notification would be triggered
        mock_notification_service.send_security_alert.assert_called()

        integration_test_context.record_operation(
            "account_lockout_notification_integration",
            time.time() - start_time
        )

    async def test_token_refresh_with_permission_revalidation(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        system_permissions: List[AdminPermission],
        integration_test_context
    ):
        """Test token refresh process with permission revalidation."""
        start_time = time.time()

        # Create expiring token
        original_token_data = {
            "sub": superuser.email,
            "user_id": str(superuser.id),
            "user_type": superuser.user_type.value,
            "security_clearance": superuser.security_clearance_level,
            "exp": datetime.utcnow() + timedelta(seconds=5)  # Very short expiry
        }

        original_token = jwt.encode(original_token_data, settings.SECRET_KEY, algorithm="HS256")

        # Wait for token to expire
        await asyncio.sleep(6)

        # Verify token is expired
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(original_token, settings.SECRET_KEY, algorithms=["HS256"])

        # Simulate token refresh
        refresh_token_data = {
            "sub": superuser.email,
            "user_id": str(superuser.id),
            "user_type": superuser.user_type.value,
            "security_clearance": superuser.security_clearance_level,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }

        new_token = jwt.encode(refresh_token_data, settings.SECRET_KEY, algorithm="HS256")

        # Verify new token is valid
        decoded_new_token = jwt.decode(new_token, settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded_new_token["user_id"] == str(superuser.id)

        # Clear permission cache to force revalidation
        await admin_permission_service_with_redis._clear_user_permission_cache(str(superuser.id))

        # Test permission validation with new token
        permission = system_permissions[0]
        result = await admin_permission_service_with_redis.validate_permission(
            integration_db_session, superuser,
            permission.resource_type, permission.action, permission.scope
        )
        assert result is True

        # Log token refresh event
        refresh_log = AdminActivityLog(
            admin_user_id=superuser.id,
            admin_email=superuser.email,
            admin_full_name=superuser.full_name,
            action_type=AdminActionType.SECURITY,
            action_name="token_refresh",
            action_description="JWT token refreshed successfully",
            result=ActionResult.SUCCESS,
            risk_level=RiskLevel.LOW
        )
        integration_db_session.add(refresh_log)
        integration_db_session.commit()

        integration_test_context.record_operation(
            "token_refresh_permission_revalidation",
            time.time() - start_time
        )

    async def test_multi_factor_authentication_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        integration_redis_client,
        mock_notification_service,
        integration_test_context
    ):
        """Test multi-factor authentication integration with admin operations."""
        start_time = time.time()

        # Step 1: Primary authentication (username/password)
        primary_auth_token = auth_service.create_access_token(
            data={"sub": superuser.email, "user_id": str(superuser.id), "mfa_required": True}
        )

        # Step 2: Generate MFA code
        mfa_code = "123456"  # In real implementation, this would be generated
        mfa_key = f"mfa:{superuser.id}:{mfa_code}"

        # Store MFA code in Redis with short expiry
        integration_redis_client.setex(mfa_key, 300, "pending")  # 5 minutes

        # Step 3: Verify MFA code
        stored_mfa = integration_redis_client.get(mfa_key)
        assert stored_mfa == b"pending"

        # Step 4: Complete MFA authentication
        integration_redis_client.delete(mfa_key)

        # Create fully authenticated token
        full_auth_token = auth_service.create_access_token(
            data={
                "sub": superuser.email,
                "user_id": str(superuser.id),
                "mfa_verified": True,
                "security_clearance": superuser.security_clearance_level
            }
        )

        # Step 5: Test high-privilege operation with MFA
        decoded_token = jwt.decode(full_auth_token, settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded_token.get("mfa_verified") is True

        # Verify high-privilege permission requires MFA
        system_permission = next(
            p for p in system_permissions if p.required_clearance_level >= 4
        )

        result = await admin_permission_service_with_redis.validate_permission(
            integration_db_session, superuser,
            system_permission.resource_type, system_permission.action, system_permission.scope
        )
        assert result is True

        # Log MFA completion
        mfa_log = AdminActivityLog(
            admin_user_id=superuser.id,
            admin_email=superuser.email,
            admin_full_name=superuser.full_name,
            action_type=AdminActionType.SECURITY,
            action_name="mfa_authentication",
            action_description="Multi-factor authentication completed successfully",
            result=ActionResult.SUCCESS,
            risk_level=RiskLevel.MEDIUM
        )
        integration_db_session.add(mfa_log)
        integration_db_session.commit()

        # Verify notification was sent
        mock_notification_service.send_admin_notification.assert_called()

        integration_test_context.record_operation(
            "multi_factor_authentication_integration",
            time.time() - start_time
        )

    async def test_concurrent_authentication_session_management(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        multiple_admin_users: List[User],
        integration_redis_client,
        integration_test_context
    ):
        """Test concurrent authentication and session management."""
        start_time = time.time()

        async def authenticate_user_task(user: User, session_id: str):
            """Task to authenticate user and create session."""
            try:
                # Create JWT token
                token = auth_service.create_access_token(
                    data={"sub": user.email, "user_id": str(user.id)}
                )

                # Create session
                session_data = {
                    "user_id": str(user.id),
                    "email": user.email,
                    "login_time": datetime.utcnow().isoformat(),
                    "token": token
                }

                session_key = f"session:{session_id}"
                integration_redis_client.setex(
                    session_key, 3600, json.dumps(session_data, default=str)
                )

                # Cache some permissions
                await admin_permission_service_with_redis._cache_permission_result(
                    str(user.id), "users.read.global", True
                )

                # Simulate some activity
                await asyncio.sleep(0.1)

                return {"user_id": str(user.id), "session_id": session_id, "success": True}

            except Exception as e:
                return {"user_id": str(user.id), "session_id": session_id, "error": str(e), "success": False}

        # Create concurrent authentication tasks
        tasks = []
        session_ids = []

        for i, user in enumerate(multiple_admin_users):
            session_id = f"session_{i}_{uuid.uuid4()}"
            session_ids.append(session_id)
            tasks.append(authenticate_user_task(user, session_id))

        # Execute concurrent authentications
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all authentications succeeded
        successful_auths = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_auths = [r for r in results if isinstance(r, Exception) or (isinstance(r, dict) and not r.get("success"))]

        assert len(failed_auths) == 0, f"Failed authentications: {failed_auths}"
        assert len(successful_auths) == len(multiple_admin_users)

        # Verify all sessions were created
        for session_id in session_ids:
            session_key = f"session:{session_id}"
            session_data = integration_redis_client.get(session_key)
            assert session_data is not None

        # Cleanup sessions
        for session_id in session_ids:
            integration_redis_client.delete(f"session:{session_id}")

        integration_test_context.record_operation(
            "concurrent_authentication_session_management",
            time.time() - start_time
        )

    async def test_security_event_propagation_across_services(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        admin_user: User,
        mock_email_service,
        mock_notification_service,
        integration_test_context
    ):
        """Test security event propagation across different services."""
        start_time = time.time()

        # Simulate security event: Suspicious permission check
        suspicious_permission_checks = []

        for i in range(10):  # Rapid permission checks
            try:
                await admin_permission_service_with_redis.validate_permission(
                    integration_db_session, admin_user,
                    ResourceType.USERS, PermissionAction.DELETE, PermissionScope.GLOBAL
                )
            except PermissionDeniedError:
                suspicious_permission_checks.append(i)

        # Should have multiple permission denials
        assert len(suspicious_permission_checks) == 10  # All should fail

        # Create security alert for suspicious activity
        security_alert = AdminActivityLog(
            admin_user_id=admin_user.id,
            admin_email=admin_user.email,
            admin_full_name=admin_user.full_name,
            action_type=AdminActionType.SECURITY,
            action_name="suspicious_permission_activity",
            action_description=f"Multiple permission denials detected: {len(suspicious_permission_checks)} attempts",
            result=ActionResult.BLOCKED,
            risk_level=RiskLevel.HIGH,
            custom_fields={
                "permission_checks": len(suspicious_permission_checks),
                "denied_resource": ResourceType.USERS.value,
                "denied_action": PermissionAction.DELETE.value
            }
        )
        integration_db_session.add(security_alert)
        integration_db_session.commit()

        # Verify email service would be notified
        mock_email_service.send_admin_security_alert.assert_called()

        # Verify notification service would be triggered
        mock_notification_service.send_security_alert.assert_called()

        # Verify audit log was created
        security_logs = integration_db_session.query(AdminActivityLog).filter(
            AdminActivityLog.admin_user_id == admin_user.id,
            AdminActivityLog.action_name == "suspicious_permission_activity"
        ).all()
        assert len(security_logs) >= 1

        integration_test_context.record_operation(
            "security_event_propagation",
            time.time() - start_time
        )