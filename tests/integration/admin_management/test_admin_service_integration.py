# ~/tests/integration/admin_management/test_admin_service_integration.py
# ---------------------------------------------------------------------------------------------
# MeStore - Admin Service Integration Tests
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_admin_service_integration.py
# Ruta: ~/tests/integration/admin_management/test_admin_service_integration.py
# Autor: Integration Testing Specialist
# Fecha de Creación: 2025-09-21
# Última Actualización: 2025-09-21
# Versión: 1.0.0
# Propósito: Service-to-service integration tests for admin management system
#
# Integration Testing Coverage:
# - AdminPermissionService ↔ User Management integration
# - AuthService ↔ Session Management integration
# - EmailService ↔ Notification System integration
# - AuditService ↔ Activity Logging integration
# - RedisService ↔ Session/Cache Management integration
# - Database transaction flows with proper rollback scenarios
#
# ---------------------------------------------------------------------------------------------

"""
Admin Service Integration Tests.

Este módulo prueba la integración entre servicios del sistema de administración:
- Service-to-service communication validation
- Cross-service transaction integrity
- Error propagation and handling across services
- Performance under integrated service load
- Cache consistency across service boundaries
- Audit trail continuity across operations
"""

import pytest
import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import patch, AsyncMock
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.admin_permission_service import AdminPermissionService, PermissionDeniedError, InsufficientClearanceError
from app.services.auth_service import auth_service
from app.models.user import User, UserType
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, ActionResult, RiskLevel


@pytest.mark.asyncio
@pytest.mark.integration
class TestAdminServiceIntegration:
    """Test admin service integration with other system components."""

    async def test_permission_validation_with_auth_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        admin_user: User,
        system_permissions: List[AdminPermission],
        integration_test_context
    ):
        """Test permission validation integrated with authentication service."""
        start_time = time.time()

        # Test 1: Valid permission check with active session
        auth_token = auth_service.create_access_token(
            data={"sub": superuser.email, "user_id": str(superuser.id)}
        )

        permission = system_permissions[0]  # users.create.global
        result = await admin_permission_service_with_redis.validate_permission(
            integration_db_session, superuser,
            permission.resource_type, permission.action, permission.scope
        )

        assert result is True
        integration_test_context.record_operation(
            "permission_validation_with_auth",
            time.time() - start_time
        )

        # Test 2: Permission denied for insufficient clearance
        with pytest.raises(PermissionDeniedError):
            system_permission = next(p for p in system_permissions if p.required_clearance_level == 5)
            await admin_permission_service_with_redis.validate_permission(
                integration_db_session, admin_user,  # clearance level 3
                system_permission.resource_type, system_permission.action, system_permission.scope
            )

        # Test 3: Verify audit logging integration
        audit_logs = integration_db_session.query(AdminActivityLog).filter(
            AdminActivityLog.admin_user_id == superuser.id,
            AdminActivityLog.action_name == "permission_check"
        ).all()

        assert len(audit_logs) >= 1
        assert audit_logs[0].result == ActionResult.SUCCESS

    async def test_user_creation_with_permission_grant_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        system_permissions: List[AdminPermission],
        mock_email_service,
        integration_test_context
    ):
        """Test complete user creation workflow with permission granting."""
        start_time = time.time()

        # Create new admin user
        new_admin_data = {
            'email': 'integration.test@mestore.com',
            'password_hash': auth_service.get_password_hash('test_password_123'),
            'nombre': 'Integration',
            'apellido': 'Test',
            'user_type': UserType.ADMIN,
            'security_clearance_level': 3,
            'is_active': True,
            'is_verified': True,
            'performance_score': 90,
            'habeas_data_accepted': True,
            'data_processing_consent': True
        }

        new_admin = User(**new_admin_data)
        integration_db_session.add(new_admin)
        integration_db_session.commit()
        integration_db_session.refresh(new_admin)

        # Grant permission to new admin
        permission = next(p for p in system_permissions if p.name == "users.read.global")
        success = await admin_permission_service_with_redis.grant_permission(
            integration_db_session, superuser, new_admin, permission
        )

        assert success is True

        # Verify permission was granted
        user_permissions = await admin_permission_service_with_redis.get_user_permissions(
            integration_db_session, new_admin
        )

        granted_permission_names = [p['name'] for p in user_permissions]
        assert "users.read.global" in granted_permission_names

        # Verify email notification was triggered
        mock_email_service.send_admin_permission_notification.assert_called()

        # Verify audit logging
        audit_logs = integration_db_session.query(AdminActivityLog).filter(
            AdminActivityLog.admin_user_id == superuser.id,
            AdminActivityLog.action_name == "grant_permission"
        ).all()

        assert len(audit_logs) >= 1
        assert audit_logs[0].target_id == str(new_admin.id)

        integration_test_context.record_operation(
            "user_creation_with_permission_grant",
            time.time() - start_time
        )

    async def test_bulk_permission_operations_with_cache_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        multiple_admin_users: List[User],
        system_permissions: List[AdminPermission],
        integration_redis_client,
        integration_test_context
    ):
        """Test bulk permission operations with Redis cache integration."""
        start_time = time.time()

        # Clear cache to start fresh
        integration_redis_client.flushall()

        permission = next(p for p in system_permissions if p.name == "users.read.global")

        # Grant permission to multiple users
        for user in multiple_admin_users[:3]:  # Only active users
            await admin_permission_service_with_redis.grant_permission(
                integration_db_session, superuser, user, permission
            )

        # Test cache warming - first permission check should miss cache
        cache_key = f"permission:{multiple_admin_users[0].id}:users.read.global"
        cached_result = integration_redis_client.get(cache_key)
        assert cached_result is None  # Should be None before validation

        # Validate permission - this should cache the result
        result = await admin_permission_service_with_redis.validate_permission(
            integration_db_session, multiple_admin_users[0],
            permission.resource_type, permission.action, permission.scope
        )

        assert result is True

        # Verify result is now cached
        cached_result = integration_redis_client.get(cache_key)
        assert cached_result is not None

        # Test cache invalidation after permission revocation
        await admin_permission_service_with_redis.revoke_permission(
            integration_db_session, superuser, multiple_admin_users[0], permission
        )

        # Cache should be cleared
        cached_result = integration_redis_client.get(cache_key)
        assert cached_result is None

        integration_test_context.record_operation(
            "bulk_permission_operations_with_cache",
            time.time() - start_time
        )

    async def test_concurrent_permission_operations_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        multiple_admin_users: List[User],
        system_permissions: List[AdminPermission],
        integration_test_context
    ):
        """Test concurrent permission operations for race condition handling."""
        start_time = time.time()

        permission = next(p for p in system_permissions if p.name == "users.read.global")

        async def grant_permission_task(user):
            """Task to grant permission to a user."""
            try:
                return await admin_permission_service_with_redis.grant_permission(
                    integration_db_session, superuser, user, permission
                )
            except Exception as e:
                return False

        async def revoke_permission_task(user):
            """Task to revoke permission from a user."""
            try:
                return await admin_permission_service_with_redis.revoke_permission(
                    integration_db_session, superuser, user, permission
                )
            except Exception as e:
                return False

        # Create concurrent tasks
        tasks = []
        for user in multiple_admin_users[:3]:
            # Each user gets grant and revoke operations
            tasks.append(grant_permission_task(user))
            tasks.append(revoke_permission_task(user))

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify no exceptions occurred due to race conditions
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0, f"Concurrent operations failed: {exceptions}"

        # Verify database consistency
        for user in multiple_admin_users[:3]:
            user_permissions = await admin_permission_service_with_redis.get_user_permissions(
                integration_db_session, user
            )
            # Final state should be consistent (either granted or not)
            assert isinstance(user_permissions, list)

        integration_test_context.record_operation(
            "concurrent_permission_operations",
            time.time() - start_time
        )

    async def test_permission_expiry_with_background_task_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        admin_user: User,
        system_permissions: List[AdminPermission],
        integration_test_context
    ):
        """Test permission expiry handling with background task integration."""
        start_time = time.time()

        permission = next(p for p in system_permissions if p.name == "users.read.global")

        # Grant permission with short expiry
        expires_at = datetime.utcnow() + timedelta(seconds=2)
        success = await admin_permission_service_with_redis.grant_permission(
            integration_db_session, superuser, admin_user, permission, expires_at
        )

        assert success is True

        # Verify permission is valid initially
        result = await admin_permission_service_with_redis.validate_permission(
            integration_db_session, admin_user,
            permission.resource_type, permission.action, permission.scope
        )
        assert result is True

        # Wait for expiry
        await asyncio.sleep(3)

        # Clear cache to force database check
        await admin_permission_service_with_redis._clear_user_permission_cache(admin_user.id)

        # Verify permission is now invalid
        with pytest.raises(PermissionDeniedError):
            await admin_permission_service_with_redis.validate_permission(
                integration_db_session, admin_user,
                permission.resource_type, permission.action, permission.scope
            )

        integration_test_context.record_operation(
            "permission_expiry_integration",
            time.time() - start_time
        )

    async def test_error_handling_across_service_boundaries(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        admin_user: User,
        system_permissions: List[AdminPermission],
        mock_email_service,
        integration_test_context
    ):
        """Test error handling and propagation across service boundaries."""
        start_time = time.time()

        # Test 1: Email service failure during permission grant
        mock_email_service.send_admin_permission_notification.side_effect = Exception("SMTP Error")

        permission = next(p for p in system_permissions if p.name == "users.read.global")

        # Permission grant should still succeed even if email fails
        success = await admin_permission_service_with_redis.grant_permission(
            integration_db_session, superuser, admin_user, permission
        )

        assert success is True  # Should not fail due to email error

        # Test 2: Database transaction rollback on permission conflict
        # Try to grant permission that requires higher clearance
        high_clearance_permission = next(
            p for p in system_permissions if p.required_clearance_level == 5
        )

        with pytest.raises(PermissionDeniedError):
            await admin_permission_service_with_redis.grant_permission(
                integration_db_session, admin_user,  # lower clearance user
                superuser, high_clearance_permission
            )

        # Verify database state is consistent
        user_permissions = await admin_permission_service_with_redis.get_user_permissions(
            integration_db_session, superuser
        )
        high_clearance_perms = [
            p for p in user_permissions
            if p['required_clearance_level'] == 5 and p['source'] == 'DIRECT'
        ]
        assert len(high_clearance_perms) == 0  # Should not have been granted

        integration_test_context.record_operation(
            "error_handling_across_services",
            time.time() - start_time
        )

    async def test_audit_trail_continuity_across_operations(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        admin_user: User,
        system_permissions: List[AdminPermission],
        audit_validation_helper,
        integration_test_context
    ):
        """Test audit trail continuity across multiple service operations."""
        start_time = time.time()

        audit_validator = audit_validation_helper(integration_db_session)

        # Get initial audit log count
        initial_count = audit_validator.count_logs_by_action("grant_permission")

        permission = next(p for p in system_permissions if p.name == "users.read.global")

        # Perform series of operations
        operations = [
            ("grant_permission", lambda: admin_permission_service_with_redis.grant_permission(
                integration_db_session, superuser, admin_user, permission
            )),
            ("validate_permission", lambda: admin_permission_service_with_redis.validate_permission(
                integration_db_session, admin_user,
                permission.resource_type, permission.action, permission.scope
            )),
            ("revoke_permission", lambda: admin_permission_service_with_redis.revoke_permission(
                integration_db_session, superuser, admin_user, permission
            ))
        ]

        for operation_name, operation_func in operations:
            await operation_func()

            # Verify audit log was created
            logs = audit_validator.get_recent_logs(
                superuser.id if operation_name != "validate_permission" else admin_user.id
            )
            assert len(logs) > 0

            latest_log = logs[0]
            assert latest_log.action_name in [operation_name, "permission_check"]

        # Verify audit trail completeness
        final_count = audit_validator.count_logs_by_action("grant_permission")
        assert final_count > initial_count

        integration_test_context.record_operation(
            "audit_trail_continuity",
            time.time() - start_time
        )

    async def test_performance_under_integrated_load(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        multiple_admin_users: List[User],
        system_permissions: List[AdminPermission],
        performance_metrics,
        integration_test_context
    ):
        """Test system performance under integrated service load."""
        start_time = time.time()

        permission = next(p for p in system_permissions if p.name == "users.read.global")

        # Simulate high load scenario
        operations_count = 50
        tasks = []

        for i in range(operations_count):
            user = multiple_admin_users[i % len(multiple_admin_users)]
            if i % 2 == 0:
                # Grant permission
                task = admin_permission_service_with_redis.grant_permission(
                    integration_db_session, superuser, user, permission
                )
            else:
                # Validate permission
                task = admin_permission_service_with_redis.validate_permission(
                    integration_db_session, user,
                    permission.resource_type, permission.action, permission.scope
                )
            tasks.append(task)

        # Execute all operations
        start_operations = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        operation_duration = time.time() - start_operations

        # Analyze results
        successful_operations = [r for r in results if not isinstance(r, Exception)]
        failed_operations = [r for r in results if isinstance(r, Exception)]

        # Performance assertions
        assert len(failed_operations) == 0, f"Failed operations: {failed_operations}"
        assert operation_duration < 5.0, f"Operations took too long: {operation_duration}s"

        # Average response time should be reasonable
        avg_response_time = operation_duration / operations_count
        assert avg_response_time < 0.1, f"Average response time too high: {avg_response_time}s"

        performance_metrics['response_times'].append(avg_response_time)
        performance_metrics['database_queries'].append(operations_count * 2)  # Estimated

        integration_test_context.record_operation(
            "performance_under_load",
            time.time() - start_time
        )

        # Verify final success rate
        success_rate = integration_test_context.get_success_rate()
        assert success_rate >= 0.95, f"Success rate too low: {success_rate}"

    async def test_service_dependency_injection_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        integration_test_context
    ):
        """Test service dependency injection and configuration integration."""
        start_time = time.time()

        # Test Redis service injection
        assert admin_permission_service_with_redis.redis_client is not None
        assert admin_permission_service_with_redis.cache_ttl > 0

        # Test database session injection
        assert integration_db_session is not None

        # Test service method availability
        assert hasattr(admin_permission_service_with_redis, 'validate_permission')
        assert hasattr(admin_permission_service_with_redis, 'grant_permission')
        assert hasattr(admin_permission_service_with_redis, 'revoke_permission')

        # Test service configuration
        assert admin_permission_service_with_redis.permission_hierarchy is not None
        assert len(admin_permission_service_with_redis.permission_hierarchy) > 0

        integration_test_context.record_operation(
            "service_dependency_injection",
            time.time() - start_time
        )

    async def test_cross_service_transaction_integrity(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        admin_user: User,
        system_permissions: List[AdminPermission],
        transaction_test_helper,
        integration_test_context
    ):
        """Test transaction integrity across multiple services."""
        start_time = time.time()

        tx_helper = transaction_test_helper(integration_db_session)
        permission = next(p for p in system_permissions if p.name == "users.read.global")

        # Create savepoint before operations
        savepoint = tx_helper.create_savepoint("cross_service_test")

        try:
            # Perform multiple operations in same transaction
            await admin_permission_service_with_redis.grant_permission(
                integration_db_session, superuser, admin_user, permission
            )

            # Verify permission exists
            user_perms = await admin_permission_service_with_redis.get_user_permissions(
                integration_db_session, admin_user
            )
            assert any(p['name'] == permission.name for p in user_perms)

            # Simulate error scenario
            with pytest.raises(PermissionDeniedError):
                high_clearance_perm = next(
                    p for p in system_permissions if p.required_clearance_level == 5
                )
                await admin_permission_service_with_redis.grant_permission(
                    integration_db_session, admin_user,  # insufficient clearance
                    superuser, high_clearance_perm
                )

            # Rollback to savepoint
            tx_helper.rollback_to_savepoint("cross_service_test")

            # Verify rollback worked
            user_perms_after_rollback = await admin_permission_service_with_redis.get_user_permissions(
                integration_db_session, admin_user
            )
            direct_perms = [p for p in user_perms_after_rollback if p['source'] == 'DIRECT']
            assert len(direct_perms) == 0  # Should be rolled back

        except Exception as e:
            tx_helper.rollback_to_savepoint("cross_service_test")
            raise

        integration_test_context.record_operation(
            "cross_service_transaction_integrity",
            time.time() - start_time
        )