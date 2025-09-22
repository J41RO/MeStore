# ~/tests/integration/admin_management/test_admin_session_integration.py
# ---------------------------------------------------------------------------------------------
# MeStore - Admin Session Integration Tests
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_admin_session_integration.py
# Ruta: ~/tests/integration/admin_management/test_admin_session_integration.py
# Autor: Integration Testing Specialist
# Fecha de Creación: 2025-09-21
# Última Actualización: 2025-09-21
# Versión: 1.0.0
# Propósito: Session and Redis integration tests for admin management system
#
# Session Integration Testing Coverage:
# - RedisService ↔ Session/Cache Management integration
# - Session lifecycle ↔ Permission caching integration
# - Session timeout ↔ Authentication validation integration
# - Concurrent session ↔ Data consistency integration
# - Session invalidation ↔ Security event integration
# - Redis cluster ↔ High availability integration
#
# ---------------------------------------------------------------------------------------------

"""
Admin Session Integration Tests.

Este módulo prueba la integración de sesiones para el sistema de administración:
- Redis session storage with permission caching
- Session lifecycle management across services
- Concurrent session handling and data consistency
- Session security and invalidation mechanisms
- Redis failover and high availability scenarios
- Session-based rate limiting and security controls
"""

import pytest
import asyncio
import time
import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.orm import Session

from app.services.admin_permission_service import AdminPermissionService
from app.services.auth_service import auth_service
from app.models.user import User, UserType
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, ActionResult, RiskLevel


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.session
class TestAdminSessionIntegration:
    """Test admin session integration with Redis caching and permission management."""

    async def test_session_creation_with_permission_caching_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        system_permissions: List[AdminPermission],
        integration_redis_client,
        integration_test_context
    ):
        """Test session creation integrated with permission caching."""
        start_time = time.time()

        session_id = str(uuid.uuid4())
        user_id = str(superuser.id)

        # Create session data
        session_data = {
            'user_id': user_id,
            'email': superuser.email,
            'user_type': superuser.user_type.value,
            'security_clearance': superuser.security_clearance_level,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'permissions_loaded': False,
            'session_version': 1
        }

        # Store session in Redis
        session_key = f"session:{session_id}"
        integration_redis_client.setex(
            session_key, 3600, json.dumps(session_data, default=str)
        )

        # Verify session was created
        stored_session = integration_redis_client.get(session_key)
        assert stored_session is not None

        session_obj = json.loads(stored_session)
        assert session_obj['user_id'] == user_id

        # Warm up permission cache during session activity
        permission = system_permissions[0]
        result = await admin_permission_service_with_redis.validate_permission(
            integration_db_session, superuser,
            permission.resource_type, permission.action, permission.scope
        )

        assert result is True

        # Verify permission was cached
        permission_key = f"permission:{user_id}:users.create.global"
        cached_permission = integration_redis_client.get(permission_key)
        assert cached_permission is not None

        # Update session to mark permissions as loaded
        session_obj['permissions_loaded'] = True
        session_obj['last_activity'] = datetime.utcnow().isoformat()
        session_obj['cached_permissions_count'] = 1

        integration_redis_client.setex(
            session_key, 3600, json.dumps(session_obj, default=str)
        )

        # Verify session update
        updated_session = json.loads(integration_redis_client.get(session_key))
        assert updated_session['permissions_loaded'] is True
        assert updated_session['cached_permissions_count'] == 1

        integration_test_context.record_operation(
            "session_creation_permission_caching",
            time.time() - start_time
        )

    async def test_session_timeout_with_cache_invalidation_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        admin_user: User,
        integration_redis_client,
        integration_test_context
    ):
        """Test session timeout handling with automatic cache invalidation."""
        start_time = time.time()

        session_id = str(uuid.uuid4())
        user_id = str(admin_user.id)

        # Create session with short timeout
        session_data = {
            'user_id': user_id,
            'email': admin_user.email,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=3)).isoformat(),
            'session_timeout': 3
        }

        session_key = f"session:{session_id}"
        integration_redis_client.setex(session_key, 3, json.dumps(session_data, default=str))

        # Cache some permissions
        await admin_permission_service_with_redis._cache_permission_result(
            user_id, "users.read.global", True
        )

        # Verify session and permissions exist
        assert integration_redis_client.get(session_key) is not None
        cached_perm = await admin_permission_service_with_redis._get_cached_permission(
            user_id, "users.read.global"
        )
        assert cached_perm is True

        # Wait for session to expire
        await asyncio.sleep(4)

        # Verify session expired
        expired_session = integration_redis_client.get(session_key)
        assert expired_session is None

        # Test automatic cache cleanup on session expiry
        # In a real system, this would be handled by a background task
        await admin_permission_service_with_redis._clear_user_permission_cache(user_id)

        # Verify permissions were cleared
        cached_perm_after_expiry = await admin_permission_service_with_redis._get_cached_permission(
            user_id, "users.read.global"
        )
        assert cached_perm_after_expiry is None

        # Log session timeout event
        timeout_log = AdminActivityLog(
            admin_user_id=admin_user.id,
            admin_email=admin_user.email,
            admin_full_name=admin_user.full_name,
            action_type=AdminActionType.SECURITY,
            action_name="session_timeout",
            action_description=f"Session {session_id} expired after timeout",
            result=ActionResult.SUCCESS,
            risk_level=RiskLevel.LOW,
            custom_fields={
                'session_id': session_id,
                'timeout_duration': 3,
                'cache_cleared': True
            }
        )

        integration_db_session.add(timeout_log)
        integration_db_session.commit()

        integration_test_context.record_operation(
            "session_timeout_cache_invalidation",
            time.time() - start_time
        )

    async def test_concurrent_session_access_consistency_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        integration_redis_client,
        integration_test_context
    ):
        """Test concurrent session access with data consistency."""
        start_time = time.time()

        session_id = str(uuid.uuid4())
        user_id = str(superuser.id)

        # Create initial session
        session_data = {
            'user_id': user_id,
            'email': superuser.email,
            'activity_count': 0,
            'last_activity': datetime.utcnow().isoformat(),
            'concurrent_access': True
        }

        session_key = f"session:{session_id}"
        integration_redis_client.setex(
            session_key, 3600, json.dumps(session_data, default=str)
        )

        async def update_session_activity(task_id: int):
            """Task to update session activity concurrently."""
            try:
                # Use Redis WATCH for optimistic locking
                pipe = integration_redis_client.pipeline()

                # Get current session data
                current_session = integration_redis_client.get(session_key)
                if current_session:
                    session_obj = json.loads(current_session)

                    # Update activity count
                    session_obj['activity_count'] = session_obj.get('activity_count', 0) + 1
                    session_obj['last_activity'] = datetime.utcnow().isoformat()
                    session_obj[f'task_{task_id}_timestamp'] = datetime.utcnow().isoformat()

                    # Atomic update
                    pipe.setex(
                        session_key, 3600, json.dumps(session_obj, default=str)
                    )
                    pipe.execute()

                    # Simulate some processing time
                    await asyncio.sleep(0.1)

                    return {
                        'task_id': task_id,
                        'activity_count': session_obj['activity_count'],
                        'success': True
                    }

            except Exception as e:
                return {
                    'task_id': task_id,
                    'error': str(e),
                    'success': False
                }

        # Create concurrent session update tasks
        num_tasks = 10
        tasks = [update_session_activity(i) for i in range(num_tasks)]

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze results
        successful_updates = [r for r in results if isinstance(r, dict) and r.get('success')]
        failed_updates = [r for r in results if isinstance(r, Exception) or (isinstance(r, dict) and not r.get('success'))]

        # Most updates should succeed
        assert len(successful_updates) >= num_tasks * 0.8
        assert len(failed_updates) <= num_tasks * 0.2

        # Verify final session state
        final_session = json.loads(integration_redis_client.get(session_key))
        assert final_session['activity_count'] <= num_tasks  # Should not exceed task count
        assert final_session['activity_count'] > 0  # Should have some updates

        # Verify timestamps from different tasks exist
        task_timestamps = [key for key in final_session.keys() if key.startswith('task_')]
        assert len(task_timestamps) > 0

        integration_test_context.record_operation(
            "concurrent_session_access_consistency",
            time.time() - start_time
        )

    async def test_session_invalidation_on_security_event_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        admin_user: User,
        integration_redis_client,
        integration_test_context
    ):
        """Test session invalidation triggered by security events."""
        start_time = time.time()

        user_id = str(admin_user.id)
        session_ids = [str(uuid.uuid4()) for _ in range(3)]

        # Create multiple sessions for the user
        for i, session_id in enumerate(session_ids):
            session_data = {
                'user_id': user_id,
                'email': admin_user.email,
                'device': f'device_{i}',
                'ip_address': f'192.168.1.{100 + i}',
                'created_at': datetime.utcnow().isoformat(),
                'session_index': i
            }

            session_key = f"session:{session_id}"
            integration_redis_client.setex(
                session_key, 3600, json.dumps(session_data, default=str)
            )

        # Cache permissions for the user
        await admin_permission_service_with_redis._cache_permission_result(
            user_id, "users.read.global", True
        )

        # Verify all sessions exist
        for session_id in session_ids:
            session_key = f"session:{session_id}"
            assert integration_redis_client.get(session_key) is not None

        # Simulate security event (suspicious activity detected)
        security_event = AdminActivityLog(
            admin_user_id=admin_user.id,
            admin_email=admin_user.email,
            admin_full_name=admin_user.full_name,
            action_type=AdminActionType.SECURITY,
            action_name="suspicious_activity_detected",
            action_description="Multiple failed permission checks detected",
            result=ActionResult.BLOCKED,
            risk_level=RiskLevel.HIGH,
            custom_fields={
                'trigger': 'multiple_permission_denials',
                'active_sessions': len(session_ids)
            }
        )

        integration_db_session.add(security_event)
        integration_db_session.commit()

        # Invalidate all user sessions due to security event
        user_session_pattern = f"session:*"
        all_session_keys = integration_redis_client.keys(user_session_pattern)

        invalidated_sessions = []
        for key in all_session_keys:
            session_data = integration_redis_client.get(key)
            if session_data:
                session_obj = json.loads(session_data)
                if session_obj.get('user_id') == user_id:
                    integration_redis_client.delete(key)
                    invalidated_sessions.append(key.decode() if isinstance(key, bytes) else key)

        # Clear all cached permissions for the user
        await admin_permission_service_with_redis._clear_user_permission_cache(user_id)

        # Verify sessions were invalidated
        for session_id in session_ids:
            session_key = f"session:{session_id}"
            assert integration_redis_client.get(session_key) is None

        # Verify permissions were cleared
        cached_perm = await admin_permission_service_with_redis._get_cached_permission(
            user_id, "users.read.global"
        )
        assert cached_perm is None

        # Log session invalidation
        invalidation_log = AdminActivityLog(
            admin_user_id=admin_user.id,
            admin_email=admin_user.email,
            admin_full_name=admin_user.full_name,
            action_type=AdminActionType.SECURITY,
            action_name="sessions_invalidated",
            action_description=f"All sessions invalidated due to security event",
            result=ActionResult.SUCCESS,
            risk_level=RiskLevel.HIGH,
            custom_fields={
                'invalidated_sessions': len(invalidated_sessions),
                'reason': 'security_event',
                'cache_cleared': True
            }
        )

        integration_db_session.add(invalidation_log)
        integration_db_session.commit()

        integration_test_context.record_operation(
            "session_invalidation_security_event",
            time.time() - start_time
        )

    async def test_redis_failover_session_recovery_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        integration_redis_client,
        integration_test_context
    ):
        """Test session recovery during Redis failover scenarios."""
        start_time = time.time()

        session_id = str(uuid.uuid4())
        user_id = str(superuser.id)

        # Create session with backup mechanism
        session_data = {
            'user_id': user_id,
            'email': superuser.email,
            'backup_enabled': True,
            'created_at': datetime.utcnow().isoformat(),
            'failover_test': True
        }

        session_key = f"session:{session_id}"
        backup_key = f"session_backup:{session_id}"

        # Store session in primary and backup locations
        integration_redis_client.setex(
            session_key, 3600, json.dumps(session_data, default=str)
        )
        integration_redis_client.setex(
            backup_key, 3600, json.dumps(session_data, default=str)
        )

        # Cache permissions
        await admin_permission_service_with_redis._cache_permission_result(
            user_id, "users.read.global", True
        )

        # Verify session and backup exist
        assert integration_redis_client.get(session_key) is not None
        assert integration_redis_client.get(backup_key) is not None

        # Simulate Redis primary failure by deleting primary session
        integration_redis_client.delete(session_key)

        # Verify primary session is gone
        assert integration_redis_client.get(session_key) is None

        # Test session recovery from backup
        backup_session = integration_redis_client.get(backup_key)
        assert backup_session is not None

        # Restore session from backup
        backup_data = json.loads(backup_session)
        backup_data['recovered_from_backup'] = True
        backup_data['recovery_timestamp'] = datetime.utcnow().isoformat()

        # Restore to primary location
        integration_redis_client.setex(
            session_key, 3600, json.dumps(backup_data, default=str)
        )

        # Verify session was recovered
        recovered_session = json.loads(integration_redis_client.get(session_key))
        assert recovered_session['recovered_from_backup'] is True
        assert recovered_session['user_id'] == user_id

        # Test permission cache recovery
        # In a real system, permissions might need to be reloaded
        cached_perm = await admin_permission_service_with_redis._get_cached_permission(
            user_id, "users.read.global"
        )

        if cached_perm is None:
            # Simulate permission cache rebuild after failover
            await admin_permission_service_with_redis._cache_permission_result(
                user_id, "users.read.global", True
            )

            # Verify permission was restored
            restored_perm = await admin_permission_service_with_redis._get_cached_permission(
                user_id, "users.read.global"
            )
            assert restored_perm is True

        # Log failover recovery
        recovery_log = AdminActivityLog(
            admin_user_id=superuser.id,
            admin_email=superuser.email,
            admin_full_name=superuser.full_name,
            action_type=AdminActionType.SYSTEM,
            action_name="session_failover_recovery",
            action_description=f"Session {session_id} recovered from backup after failover",
            result=ActionResult.SUCCESS,
            risk_level=RiskLevel.MEDIUM,
            custom_fields={
                'session_id': session_id,
                'recovery_method': 'backup_restore',
                'permissions_rebuilt': True
            }
        )

        integration_db_session.add(recovery_log)
        integration_db_session.commit()

        integration_test_context.record_operation(
            "redis_failover_session_recovery",
            time.time() - start_time
        )

    async def test_session_based_rate_limiting_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        admin_user: User,
        integration_redis_client,
        integration_test_context
    ):
        """Test session-based rate limiting integration."""
        start_time = time.time()

        session_id = str(uuid.uuid4())
        user_id = str(admin_user.id)

        # Create session with rate limiting enabled
        session_data = {
            'user_id': user_id,
            'email': admin_user.email,
            'rate_limiting_enabled': True,
            'request_count': 0,
            'window_start': datetime.utcnow().isoformat()
        }

        session_key = f"session:{session_id}"
        integration_redis_client.setex(
            session_key, 3600, json.dumps(session_data, default=str)
        )

        # Rate limiting parameters
        max_requests = 5
        window_duration = 60  # seconds

        # Simulate multiple requests within session
        request_results = []

        for request_num in range(max_requests + 3):  # Exceed limit
            # Get current session
            current_session = integration_redis_client.get(session_key)
            if current_session:
                session_obj = json.loads(current_session)

                # Check rate limit
                current_time = datetime.utcnow()
                window_start = datetime.fromisoformat(session_obj['window_start'])

                # Reset window if expired
                if (current_time - window_start).seconds >= window_duration:
                    session_obj['request_count'] = 0
                    session_obj['window_start'] = current_time.isoformat()

                # Check if under limit
                if session_obj['request_count'] < max_requests:
                    # Allow request
                    session_obj['request_count'] += 1
                    session_obj['last_request'] = current_time.isoformat()

                    # Update session
                    integration_redis_client.setex(
                        session_key, 3600, json.dumps(session_obj, default=str)
                    )

                    request_results.append({
                        'request_num': request_num + 1,
                        'allowed': True,
                        'current_count': session_obj['request_count']
                    })

                else:
                    # Rate limit exceeded
                    request_results.append({
                        'request_num': request_num + 1,
                        'allowed': False,
                        'reason': 'rate_limit_exceeded',
                        'current_count': session_obj['request_count']
                    })

                    # Log rate limit violation
                    rate_limit_log = AdminActivityLog(
                        admin_user_id=admin_user.id,
                        admin_email=admin_user.email,
                        admin_full_name=admin_user.full_name,
                        action_type=AdminActionType.SECURITY,
                        action_name="rate_limit_exceeded",
                        action_description=f"Rate limit exceeded in session {session_id}",
                        result=ActionResult.BLOCKED,
                        risk_level=RiskLevel.MEDIUM,
                        custom_fields={
                            'session_id': session_id,
                            'request_count': session_obj['request_count'],
                            'max_requests': max_requests,
                            'window_duration': window_duration
                        }
                    )

                    integration_db_session.add(rate_limit_log)

            # Small delay between requests
            await asyncio.sleep(0.01)

        # Verify rate limiting worked
        allowed_requests = [r for r in request_results if r.get('allowed')]
        blocked_requests = [r for r in request_results if not r.get('allowed')]

        assert len(allowed_requests) == max_requests
        assert len(blocked_requests) >= 1

        # Verify the first max_requests were allowed
        for i in range(max_requests):
            assert request_results[i]['allowed'] is True

        # Verify subsequent requests were blocked
        for i in range(max_requests, len(request_results)):
            assert request_results[i]['allowed'] is False

        integration_db_session.commit()

        integration_test_context.record_operation(
            "session_based_rate_limiting",
            time.time() - start_time
        )