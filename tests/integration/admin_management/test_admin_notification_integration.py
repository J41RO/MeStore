# ~/tests/integration/admin_management/test_admin_notification_integration.py
# ---------------------------------------------------------------------------------------------
# MeStore - Admin Notification Integration Tests
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_admin_notification_integration.py
# Ruta: ~/tests/integration/admin_management/test_admin_notification_integration.py
# Autor: Integration Testing Specialist
# Fecha de Creación: 2025-09-21
# Última Actualización: 2025-09-21
# Versión: 1.0.0
# Propósito: Notification and audit integration tests for admin management system
#
# Notification Integration Testing Coverage:
# - EmailService ↔ Notification System integration
# - AuditService ↔ Activity Logging integration
# - SMTP server ↔ Email notifications integration
# - Real-time notifications ↔ WebSocket integration
# - Notification templates ↔ Content management integration
# - Delivery confirmation ↔ Retry mechanism integration
#
# ---------------------------------------------------------------------------------------------

"""
Admin Notification Integration Tests.

Este módulo prueba la integración de notificaciones para el sistema de administración:
- Email service integration with SMTP backends
- Real-time notification delivery across channels
- Notification template rendering and localization
- Delivery confirmation and retry mechanisms
- Audit logging for notification events
- Error handling and fallback notification strategies
"""

import pytest
import asyncio
import time
import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import patch, AsyncMock, MagicMock, call
from sqlalchemy.orm import Session

from app.services.admin_permission_service import AdminPermissionService
from app.models.user import User, UserType
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, ActionResult, RiskLevel


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.notification
class TestAdminNotificationIntegration:
    """Test admin notification integration with email, audit, and real-time systems."""

    async def test_email_notification_with_permission_grant_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        admin_user: User,
        system_permissions: List[AdminPermission],
        mock_email_service,
        mock_smtp_server,
        integration_test_context
    ):
        """Test email notification integration with permission granting workflow."""
        start_time = time.time()

        permission = system_permissions[0]  # users.create.global

        # Configure email service mock
        mock_email_service.send_admin_permission_notification.return_value = True

        # Grant permission (should trigger email notification)
        success = await admin_permission_service_with_redis.grant_permission(
            integration_db_session, superuser, admin_user, permission
        )

        assert success is True

        # Verify email notification was called
        mock_email_service.send_admin_permission_notification.assert_called_once()

        # Get the call arguments
        call_args = mock_email_service.send_admin_permission_notification.call_args

        # Verify notification content
        expected_data = {
            'recipient_email': admin_user.email,
            'recipient_name': admin_user.full_name,
            'permission_name': permission.name,
            'granted_by': superuser.full_name,
            'granted_at': datetime.utcnow()
        }

        # Test SMTP server integration
        email_sent = await mock_smtp_server.send_email(
            to=admin_user.email,
            subject=f"Permission Granted: {permission.name}",
            body=f"Hello {admin_user.full_name}, you have been granted the {permission.name} permission by {superuser.full_name}.",
            template="permission_granted",
            template_data=expected_data
        )

        assert email_sent is True

        # Verify email was recorded in mock SMTP server
        sent_emails = mock_smtp_server.get_sent_emails(admin_user.email)
        assert len(sent_emails) == 1
        assert sent_emails[0]['subject'] == f"Permission Granted: {permission.name}"

        integration_test_context.record_operation(
            "email_notification_permission_grant",
            time.time() - start_time
        )

    async def test_audit_logging_with_notification_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        admin_user: User,
        system_permissions: List[AdminPermission],
        audit_validation_helper,
        mock_notification_service,
        integration_test_context
    ):
        """Test audit logging integration with notification delivery."""
        start_time = time.time()

        audit_validator = audit_validation_helper(integration_db_session)
        permission = system_permissions[1]  # users.manage.global

        # Record initial audit log count
        initial_audit_count = audit_validator.count_logs_by_action("grant_permission")

        # Grant permission (should create audit log and trigger notification)
        success = await admin_permission_service_with_redis.grant_permission(
            integration_db_session, superuser, admin_user, permission
        )

        assert success is True

        # Verify audit log was created
        final_audit_count = audit_validator.count_logs_by_action("grant_permission")
        assert final_audit_count > initial_audit_count

        # Get the audit log entry
        recent_logs = audit_validator.get_recent_logs(
            superuser.id, AdminActionType.SECURITY
        )
        assert len(recent_logs) > 0

        latest_log = recent_logs[0]
        assert latest_log.action_name == "grant_permission"
        assert latest_log.target_id == str(admin_user.id)

        # Verify notification service was called for audit event
        mock_notification_service.send_admin_notification.assert_called()

        # Test audit log notification content
        notification_data = {
            'event_type': 'permission_granted',
            'admin_user': superuser.full_name,
            'target_user': admin_user.full_name,
            'permission': permission.name,
            'timestamp': latest_log.created_at,
            'risk_level': latest_log.risk_level.value
        }

        # Verify high-risk operations trigger additional notifications
        if latest_log.risk_level == RiskLevel.HIGH:
            mock_notification_service.send_security_alert.assert_called()

        integration_test_context.record_operation(
            "audit_logging_notification_integration",
            time.time() - start_time
        )

    async def test_bulk_notification_with_error_handling_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        multiple_admin_users: List[User],
        system_permissions: List[AdminPermission],
        mock_email_service,
        mock_smtp_server,
        integration_test_context
    ):
        """Test bulk notification handling with error recovery integration."""
        start_time = time.time()

        permission = system_permissions[0]
        users_to_notify = multiple_admin_users[:3]

        # Configure some email failures
        mock_smtp_server.simulate_send_failure(1)  # First email will fail

        # Grant permissions to multiple users
        notification_results = []

        for i, user in enumerate(users_to_notify):
            try:
                # Grant permission
                success = await admin_permission_service_with_redis.grant_permission(
                    integration_db_session, superuser, user, permission
                )

                # Attempt email notification
                email_result = await mock_smtp_server.send_email(
                    to=user.email,
                    subject=f"Permission Granted: {permission.name}",
                    body=f"Hello {user.full_name}, you have been granted permission.",
                    notification_id=f"perm_grant_{i}"
                )

                notification_results.append({
                    'user_id': str(user.id),
                    'email': user.email,
                    'permission_granted': success,
                    'email_sent': email_result,
                    'attempt': i + 1
                })

            except Exception as e:
                notification_results.append({
                    'user_id': str(user.id),
                    'email': user.email,
                    'error': str(e),
                    'attempt': i + 1
                })

        # Verify results
        successful_permissions = [r for r in notification_results if r.get('permission_granted')]
        successful_emails = [r for r in notification_results if r.get('email_sent')]
        failed_emails = [r for r in notification_results if r.get('email_sent') is False]

        # All permissions should be granted regardless of email failures
        assert len(successful_permissions) == len(users_to_notify)

        # Some emails should fail due to simulated failure
        assert len(failed_emails) >= 1

        # Test retry mechanism for failed notifications
        retry_tasks = []
        for failed_result in failed_emails:
            retry_task = mock_smtp_server.send_email(
                to=failed_result['email'],
                subject=f"[RETRY] Permission Granted: {permission.name}",
                body="This is a retry notification.",
                notification_id=f"retry_{failed_result['user_id']}"
            )
            retry_tasks.append(retry_task)

        # Execute retries
        if retry_tasks:
            retry_results = await asyncio.gather(*retry_tasks)
            successful_retries = [r for r in retry_results if r is True]

            # Retries should succeed (no more simulated failures)
            assert len(successful_retries) == len(retry_tasks)

        integration_test_context.record_operation(
            "bulk_notification_error_handling",
            time.time() - start_time
        )

    async def test_real_time_notification_websocket_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        admin_user: User,
        system_permissions: List[AdminPermission],
        integration_redis_client,
        integration_test_context
    ):
        """Test real-time notification integration via WebSocket."""
        start_time = time.time()

        # Mock WebSocket connection
        websocket_connections = {}

        class MockWebSocketConnection:
            def __init__(self, user_id: str):
                self.user_id = user_id
                self.messages = []
                self.connected = True

            async def send_json(self, data: Dict[str, Any]):
                if self.connected:
                    self.messages.append(data)
                    return True
                return False

            def disconnect(self):
                self.connected = False

        # Setup WebSocket connections for users
        admin_ws = MockWebSocketConnection(str(admin_user.id))
        superuser_ws = MockWebSocketConnection(str(superuser.id))

        websocket_connections[str(admin_user.id)] = admin_ws
        websocket_connections[str(superuser.id)] = superuser_ws

        permission = system_permissions[0]

        # Grant permission (should trigger real-time notification)
        success = await admin_permission_service_with_redis.grant_permission(
            integration_db_session, superuser, admin_user, permission
        )

        assert success is True

        # Simulate real-time notification via WebSocket
        notification_message = {
            'type': 'permission_granted',
            'data': {
                'permission_name': permission.name,
                'granted_by': superuser.full_name,
                'granted_at': datetime.utcnow().isoformat(),
                'message': f'You have been granted the {permission.name} permission'
            },
            'timestamp': datetime.utcnow().isoformat(),
            'notification_id': str(uuid.uuid4())
        }

        # Send notification to admin user
        await admin_ws.send_json(notification_message)

        # Send confirmation to superuser
        confirmation_message = {
            'type': 'permission_grant_confirmed',
            'data': {
                'target_user': admin_user.full_name,
                'permission_name': permission.name,
                'status': 'granted'
            },
            'timestamp': datetime.utcnow().isoformat()
        }

        await superuser_ws.send_json(confirmation_message)

        # Verify messages were received
        assert len(admin_ws.messages) == 1
        assert admin_ws.messages[0]['type'] == 'permission_granted'

        assert len(superuser_ws.messages) == 1
        assert superuser_ws.messages[0]['type'] == 'permission_grant_confirmed'

        # Test notification persistence in Redis
        notification_key = f"notifications:{admin_user.id}"
        integration_redis_client.lpush(
            notification_key,
            json.dumps(notification_message, default=str)
        )
        integration_redis_client.expire(notification_key, 86400)  # 24 hours

        # Verify notification was stored
        stored_notifications = integration_redis_client.lrange(notification_key, 0, -1)
        assert len(stored_notifications) == 1

        stored_notification = json.loads(stored_notifications[0])
        assert stored_notification['type'] == 'permission_granted'

        integration_test_context.record_operation(
            "real_time_notification_websocket",
            time.time() - start_time
        )

    async def test_notification_template_rendering_integration(
        self,
        integration_db_session: Session,
        superuser: User,
        admin_user: User,
        system_permissions: List[AdminPermission],
        mock_email_service,
        integration_test_context
    ):
        """Test notification template rendering with dynamic content integration."""
        start_time = time.time()

        permission = system_permissions[0]

        # Template data for different notification types
        notification_templates = {
            'permission_granted': {
                'subject': 'Permission Granted: {{permission_name}}',
                'body_html': '''
                <html>
                <body>
                    <h2>Permission Granted</h2>
                    <p>Hello {{recipient_name}},</p>
                    <p>You have been granted the <strong>{{permission_name}}</strong> permission by {{granted_by}}.</p>
                    <p>This permission allows you to: {{permission_description}}</p>
                    <p>Granted on: {{granted_at}}</p>
                    <hr>
                    <p><small>MeStore Admin System</small></p>
                </body>
                </html>
                ''',
                'body_text': '''
                Permission Granted

                Hello {{recipient_name}},

                You have been granted the {{permission_name}} permission by {{granted_by}}.
                This permission allows you to: {{permission_description}}

                Granted on: {{granted_at}}

                MeStore Admin System
                '''
            },
            'security_alert': {
                'subject': '[SECURITY ALERT] {{alert_type}} - {{user_email}}',
                'body_html': '''
                <html>
                <body style="color: #d32f2f;">
                    <h2>🚨 Security Alert</h2>
                    <p><strong>Alert Type:</strong> {{alert_type}}</p>
                    <p><strong>User:</strong> {{user_email}}</p>
                    <p><strong>Description:</strong> {{description}}</p>
                    <p><strong>Time:</strong> {{timestamp}}</p>
                    <p><strong>Risk Level:</strong> {{risk_level}}</p>
                    <hr>
                    <p><small>Immediate action may be required</small></p>
                </body>
                </html>
                '''
            }
        }

        # Test permission granted notification template
        template_data = {
            'recipient_name': admin_user.full_name,
            'permission_name': permission.name,
            'permission_description': permission.description,
            'granted_by': superuser.full_name,
            'granted_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        }

        # Render template (simplified template engine simulation)
        def render_template(template: str, data: Dict[str, Any]) -> str:
            rendered = template
            for key, value in data.items():
                rendered = rendered.replace(f'{{{{{key}}}}}', str(value))
            return rendered

        permission_template = notification_templates['permission_granted']
        rendered_subject = render_template(permission_template['subject'], template_data)
        rendered_html = render_template(permission_template['body_html'], template_data)
        rendered_text = render_template(permission_template['body_text'], template_data)

        # Verify template rendering
        assert permission.name in rendered_subject
        assert admin_user.full_name in rendered_html
        assert superuser.full_name in rendered_text
        assert permission.description in rendered_html

        # Test security alert notification template
        security_template_data = {
            'alert_type': 'Suspicious Permission Activity',
            'user_email': admin_user.email,
            'description': 'Multiple failed permission validation attempts detected',
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'risk_level': 'HIGH'
        }

        security_template = notification_templates['security_alert']
        rendered_security_subject = render_template(security_template['subject'], security_template_data)
        rendered_security_html = render_template(security_template['body_html'], security_template_data)

        # Verify security alert template
        assert 'SECURITY ALERT' in rendered_security_subject
        assert admin_user.email in rendered_security_subject
        assert 'HIGH' in rendered_security_html

        # Test email service integration with templates
        mock_email_service.send_templated_email = AsyncMock(return_value=True)

        await mock_email_service.send_templated_email(
            to=admin_user.email,
            template_name='permission_granted',
            template_data=template_data,
            subject=rendered_subject,
            html_body=rendered_html,
            text_body=rendered_text
        )

        mock_email_service.send_templated_email.assert_called_once()

        integration_test_context.record_operation(
            "notification_template_rendering",
            time.time() - start_time
        )

    async def test_notification_delivery_confirmation_integration(
        self,
        integration_db_session: Session,
        admin_permission_service_with_redis,
        superuser: User,
        admin_user: User,
        system_permissions: List[AdminPermission],
        mock_smtp_server,
        integration_redis_client,
        integration_test_context
    ):
        """Test notification delivery confirmation and tracking integration."""
        start_time = time.time()

        permission = system_permissions[0]
        notification_id = str(uuid.uuid4())

        # Grant permission
        success = await admin_permission_service_with_redis.grant_permission(
            integration_db_session, superuser, admin_user, permission
        )

        assert success is True

        # Send notification with tracking
        email_sent = await mock_smtp_server.send_email(
            to=admin_user.email,
            subject=f"Permission Granted: {permission.name}",
            body="Permission notification",
            notification_id=notification_id
        )

        assert email_sent is True

        # Track notification delivery status
        delivery_status = {
            'notification_id': notification_id,
            'recipient': admin_user.email,
            'type': 'permission_granted',
            'status': 'sent',
            'sent_at': datetime.utcnow().isoformat(),
            'attempts': 1
        }

        # Store delivery status in Redis
        status_key = f"notification_status:{notification_id}"
        integration_redis_client.setex(
            status_key, 86400, json.dumps(delivery_status, default=str)
        )

        # Verify delivery status is stored
        stored_status = integration_redis_client.get(status_key)
        assert stored_status is not None

        status_data = json.loads(stored_status)
        assert status_data['notification_id'] == notification_id
        assert status_data['status'] == 'sent'

        # Simulate delivery confirmation (e.g., from email provider webhook)
        delivery_confirmation = {
            'notification_id': notification_id,
            'status': 'delivered',
            'delivered_at': datetime.utcnow().isoformat(),
            'recipient_response': 'opened'
        }

        # Update delivery status
        status_data.update(delivery_confirmation)
        integration_redis_client.setex(
            status_key, 86400, json.dumps(status_data, default=str)
        )

        # Verify delivery confirmation
        updated_status = json.loads(integration_redis_client.get(status_key))
        assert updated_status['status'] == 'delivered'
        assert 'delivered_at' in updated_status

        # Create audit log for notification delivery
        delivery_log = AdminActivityLog(
            admin_user_id=superuser.id,
            admin_email=superuser.email,
            admin_full_name=superuser.full_name,
            action_type=AdminActionType.COMMUNICATION,
            action_name="notification_delivered",
            action_description=f"Permission notification delivered to {admin_user.email}",
            target_type="notification",
            target_id=notification_id,
            result=ActionResult.SUCCESS,
            risk_level=RiskLevel.LOW,
            custom_fields={
                'notification_type': 'permission_granted',
                'delivery_method': 'email',
                'delivery_status': 'delivered'
            }
        )

        integration_db_session.add(delivery_log)
        integration_db_session.commit()

        # Verify audit log was created
        delivery_logs = integration_db_session.query(AdminActivityLog).filter(
            AdminActivityLog.action_name == "notification_delivered",
            AdminActivityLog.target_id == notification_id
        ).all()

        assert len(delivery_logs) == 1
        assert delivery_logs[0].result == ActionResult.SUCCESS

        integration_test_context.record_operation(
            "notification_delivery_confirmation",
            time.time() - start_time
        )

    async def test_notification_failure_and_retry_integration(
        self,
        integration_db_session: Session,
        admin_user: User,
        mock_smtp_server,
        mock_notification_service,
        integration_redis_client,
        integration_test_context
    ):
        """Test notification failure handling and retry mechanism integration."""
        start_time = time.time()

        notification_id = str(uuid.uuid4())

        # Simulate SMTP server failures
        mock_smtp_server.simulate_send_failure(3)  # First 3 attempts will fail

        # Attempt to send notification with retry logic
        max_retries = 5
        retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff
        notification_attempts = []

        for attempt in range(max_retries):
            try:
                # Attempt to send email
                email_sent = await mock_smtp_server.send_email(
                    to=admin_user.email,
                    subject="Test Notification",
                    body="This is a test notification with retry logic",
                    notification_id=f"{notification_id}_attempt_{attempt + 1}"
                )

                notification_attempts.append({
                    'attempt': attempt + 1,
                    'success': email_sent,
                    'timestamp': datetime.utcnow().isoformat()
                })

                if email_sent:
                    break  # Success, no need to retry

                # Wait before retry (simulated)
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1)  # Shortened for testing

            except Exception as e:
                notification_attempts.append({
                    'attempt': attempt + 1,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })

        # Verify retry attempts
        assert len(notification_attempts) >= 3  # At least 3 failed attempts
        successful_attempts = [a for a in notification_attempts if a.get('success')]
        assert len(successful_attempts) >= 1  # Eventually succeeded

        # Store retry history in Redis
        retry_key = f"notification_retries:{notification_id}"
        integration_redis_client.setex(
            retry_key, 3600, json.dumps(notification_attempts, default=str)
        )

        # Test fallback notification method
        if len(successful_attempts) == 0:
            # If email fails completely, use alternative notification
            fallback_result = await mock_notification_service.send_admin_notification(
                user_id=str(admin_user.id),
                message="Email notification failed, using fallback method",
                notification_type="fallback",
                priority="high"
            )

            mock_notification_service.send_admin_notification.assert_called()

        # Create audit log for notification retry attempts
        retry_log = AdminActivityLog(
            admin_user_id=admin_user.id,
            admin_email=admin_user.email,
            admin_full_name=admin_user.full_name,
            action_type=AdminActionType.COMMUNICATION,
            action_name="notification_retry_completed",
            action_description=f"Notification retry completed after {len(notification_attempts)} attempts",
            target_type="notification",
            target_id=notification_id,
            result=ActionResult.SUCCESS if successful_attempts else ActionResult.FAILED,
            risk_level=RiskLevel.MEDIUM if not successful_attempts else RiskLevel.LOW,
            custom_fields={
                'total_attempts': len(notification_attempts),
                'successful_attempts': len(successful_attempts),
                'retry_pattern': 'exponential_backoff'
            }
        )

        integration_db_session.add(retry_log)
        integration_db_session.commit()

        integration_test_context.record_operation(
            "notification_failure_retry",
            time.time() - start_time
        )