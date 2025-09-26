# ~/tests/integration/admin_management/fixtures/integration_fixtures.py
# ---------------------------------------------------------------------------------------------
# MeStore - Integration Test Fixtures for Admin Management
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: integration_fixtures.py
# Ruta: ~/tests/integration/admin_management/fixtures/integration_fixtures.py
# Autor: Integration Testing Specialist
# Fecha de Creación: 2025-09-21
# Última Actualización: 2025-09-21
# Versión: 1.0.0
# Propósito: Comprehensive integration test fixtures for admin management system
#
# Integration Fixtures Coverage:
# - Dynamic test data factories for realistic scenarios
# - Service integration mocking configurations
# - Performance testing data generators
# - Error scenario simulation fixtures
# - Multi-service dependency injection fixtures
# - Concurrent testing data providers
#
# ---------------------------------------------------------------------------------------------

"""
Integration Test Fixtures for Admin Management.

Este módulo proporciona fixtures avanzados para testing de integración:
- Dynamic test data generation with realistic patterns
- Service integration mock configurations
- Performance and load testing data providers
- Error scenario simulation and recovery testing
- Multi-service dependency injection and isolation
- Concurrent testing data and synchronization helpers
"""

import pytest
import uuid
import random
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Generator, Callable
from dataclasses import dataclass, field
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.orm import Session

from app.models.user import User, UserType
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, ActionResult, RiskLevel
from app.services.auth_service import AuthService

# Create auth service instance
auth_service = AuthService()


# === DATA CLASSES FOR TEST SCENARIOS ===

@dataclass
class IntegrationTestUser:
    """Enhanced user data for integration testing."""
    user: User
    initial_permissions: List[str] = field(default_factory=list)
    expected_clearance: int = 3
    session_data: Dict[str, Any] = field(default_factory=dict)
    cache_keys: List[str] = field(default_factory=list)
    concurrent_operations: int = 0


@dataclass
class PermissionTestScenario:
    """Permission testing scenario configuration."""
    name: str
    permissions: List[AdminPermission]
    target_users: List[User]
    expected_results: Dict[str, bool]
    concurrent_users: int = 1
    cache_behavior: str = "normal"  # normal, miss, hit, clear
    error_rate: float = 0.0


@dataclass
class IntegrationTestMetrics:
    """Metrics collection for integration tests."""
    operation_times: Dict[str, List[float]] = field(default_factory=dict)
    error_counts: Dict[str, int] = field(default_factory=dict)
    cache_statistics: Dict[str, int] = field(default_factory=dict)
    concurrent_operations: int = 0
    peak_memory_usage: int = 0


# === DYNAMIC TEST DATA FACTORIES ===

@pytest.fixture
def user_factory():
    """Factory for creating test users with various configurations."""

    def create_user(
        user_type: UserType = UserType.ADMIN,
        security_clearance: int = 3,
        is_active: bool = True,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> User:
        """Create a user with specified parameters."""
        base_id = str(uuid.uuid4())

        user_data = {
            'id': base_id,
            'email': f'test.user.{base_id[:8]}@mestore.com',
            'nombre': f'Test{base_id[:4]}',
            'apellido': 'User',
            'user_type': user_type,
            'security_clearance_level': security_clearance,
            'is_active': is_active,
            'is_verified': True,
            'password_hash': auth_service.get_password_hash(f'test_password_{base_id[:8]}'),
            'performance_score': random.randint(70, 100),
            'habeas_data_accepted': True,
            'data_processing_consent': True
        }

        if custom_fields:
            user_data.update(custom_fields)

        return User(**user_data)

    return create_user


@pytest.fixture
def permission_factory():
    """Factory for creating test permissions with various configurations."""

    def create_permission(
        name: Optional[str] = None,
        resource_type: ResourceType = ResourceType.USERS,
        action: PermissionAction = PermissionAction.READ,
        scope: PermissionScope = PermissionScope.USER,
        clearance_level: int = 3,
        is_inheritable: bool = True
    ) -> AdminPermission:
        """Create a permission with specified parameters."""
        base_id = str(uuid.uuid4())

        permission_data = {
            'id': base_id,
            'name': name or f'test.{resource_type.value}.{action.value}.{scope.value}',
            'description': f'Test permission for {resource_type.value} {action.value}',
            'resource_type': resource_type,
            'action': action,
            'scope': scope,
            'required_clearance_level': clearance_level,
            'is_inheritable': is_inheritable,
            'is_system_permission': False
        }

        return AdminPermission(**permission_data)

    return create_permission


@pytest.fixture
def test_scenario_factory(user_factory, permission_factory):
    """Factory for creating complete test scenarios."""

    def create_scenario(
        scenario_type: str = "basic_permission_grant",
        num_users: int = 3,
        num_permissions: int = 2,
        concurrent_operations: int = 1,
        error_simulation: bool = False
    ) -> PermissionTestScenario:
        """Create a test scenario with specified parameters."""

        # Create users
        users = []
        for i in range(num_users):
            user_type = UserType.ADMIN if i < num_users - 1 else UserType.SUPERUSER
            clearance = 3 if user_type == UserType.ADMIN else 4
            user = user_factory(
                user_type=user_type,
                security_clearance=clearance,
                custom_fields={'scenario_index': i}
            )
            users.append(user)

        # Create permissions
        permissions = []
        resource_types = [ResourceType.USERS, ResourceType.VENDORS, ResourceType.AUDIT_LOGS]
        actions = [PermissionAction.READ, PermissionAction.CREATE, PermissionAction.MANAGE]
        scopes = [PermissionScope.USER, PermissionScope.DEPARTMENT, PermissionScope.GLOBAL]

        for i in range(num_permissions):
            permission = permission_factory(
                resource_type=random.choice(resource_types),
                action=random.choice(actions),
                scope=random.choice(scopes),
                clearance_level=random.randint(2, 4)
            )
            permissions.append(permission)

        # Generate expected results based on scenario type
        expected_results = {}
        for user in users:
            for permission in permissions:
                if scenario_type == "all_granted":
                    expected_results[f"{user.id}:{permission.id}"] = True
                elif scenario_type == "clearance_based":
                    expected_results[f"{user.id}:{permission.id}"] = (
                        user.security_clearance_level >= permission.required_clearance_level
                    )
                else:  # basic_permission_grant
                    expected_results[f"{user.id}:{permission.id}"] = user.user_type == UserType.SUPERUSER

        return PermissionTestScenario(
            name=scenario_type,
            permissions=permissions,
            target_users=users,
            expected_results=expected_results,
            concurrent_users=concurrent_operations,
            error_rate=0.1 if error_simulation else 0.0
        )

    return create_scenario


# === PERFORMANCE TESTING FIXTURES ===

@pytest.fixture
def load_test_data_generator():
    """Generator for load testing data."""

    def generate_load_data(
        num_users: int = 100,
        num_permissions: int = 50,
        operations_per_user: int = 10
    ) -> Dict[str, Any]:
        """Generate data for load testing scenarios."""

        # Generate user IDs
        user_ids = [str(uuid.uuid4()) for _ in range(num_users)]

        # Generate permission IDs
        permission_ids = [str(uuid.uuid4()) for _ in range(num_permissions)]

        # Generate operation sequences
        operations = ['grant', 'revoke', 'validate', 'list']
        operation_sequences = []

        for user_id in user_ids:
            user_operations = []
            for _ in range(operations_per_user):
                operation = {
                    'type': random.choice(operations),
                    'user_id': user_id,
                    'permission_id': random.choice(permission_ids),
                    'timestamp': datetime.utcnow() + timedelta(milliseconds=random.randint(0, 10000))
                }
                user_operations.append(operation)
            operation_sequences.append(user_operations)

        return {
            'user_ids': user_ids,
            'permission_ids': permission_ids,
            'operation_sequences': operation_sequences,
            'total_operations': num_users * operations_per_user,
            'estimated_duration': (num_users * operations_per_user) * 0.01  # 10ms per operation
        }

    return generate_load_data


@pytest.fixture
def performance_monitor():
    """Performance monitoring fixture for integration tests."""

    class PerformanceMonitor:
        def __init__(self):
            self.metrics = IntegrationTestMetrics()
            self.operation_start_times = {}

        def start_operation(self, operation_name: str, operation_id: str = None):
            """Start timing an operation."""
            op_id = operation_id or str(uuid.uuid4())
            self.operation_start_times[op_id] = {
                'name': operation_name,
                'start_time': time.time()
            }
            return op_id

        def end_operation(self, operation_id: str, success: bool = True):
            """End timing an operation and record metrics."""
            if operation_id in self.operation_start_times:
                op_info = self.operation_start_times[operation_id]
                duration = time.time() - op_info['start_time']

                op_name = op_info['name']
                if op_name not in self.metrics.operation_times:
                    self.metrics.operation_times[op_name] = []
                self.metrics.operation_times[op_name].append(duration)

                if not success:
                    if op_name not in self.metrics.error_counts:
                        self.metrics.error_counts[op_name] = 0
                    self.metrics.error_counts[op_name] += 1

                del self.operation_start_times[operation_id]

        def record_cache_event(self, event_type: str):
            """Record cache-related events."""
            if event_type not in self.metrics.cache_statistics:
                self.metrics.cache_statistics[event_type] = 0
            self.metrics.cache_statistics[event_type] += 1

        def get_performance_summary(self) -> Dict[str, Any]:
            """Get performance metrics summary."""
            summary = {
                'operations': {},
                'cache_statistics': self.metrics.cache_statistics,
                'error_counts': self.metrics.error_counts
            }

            for op_name, times in self.metrics.operation_times.items():
                if times:
                    summary['operations'][op_name] = {
                        'count': len(times),
                        'avg_time': sum(times) / len(times),
                        'min_time': min(times),
                        'max_time': max(times),
                        'total_time': sum(times)
                    }

            return summary

    return PerformanceMonitor()


# === ERROR SIMULATION FIXTURES ===

@pytest.fixture
def error_injection_service():
    """Service for injecting errors during integration tests."""

    class ErrorInjectionService:
        def __init__(self):
            self.error_configs = {}
            self.error_counts = {}

        def configure_error(
            self,
            service_name: str,
            method_name: str,
            error_type: Exception = Exception,
            error_rate: float = 0.1,
            max_errors: int = None
        ):
            """Configure error injection for a service method."""
            key = f"{service_name}.{method_name}"
            self.error_configs[key] = {
                'error_type': error_type,
                'error_rate': error_rate,
                'max_errors': max_errors,
                'error_count': 0
            }
            self.error_counts[key] = 0

        def should_inject_error(self, service_name: str, method_name: str) -> bool:
            """Determine if an error should be injected."""
            key = f"{service_name}.{method_name}"

            if key not in self.error_configs:
                return False

            config = self.error_configs[key]

            # Check max errors limit
            if config['max_errors'] and config['error_count'] >= config['max_errors']:
                return False

            # Check error rate
            if random.random() < config['error_rate']:
                config['error_count'] += 1
                self.error_counts[key] += 1
                return True

            return False

        def get_error(self, service_name: str, method_name: str) -> Exception:
            """Get the configured error for injection."""
            key = f"{service_name}.{method_name}"
            if key in self.error_configs:
                error_type = self.error_configs[key]['error_type']
                return error_type(f"Injected error in {service_name}.{method_name}")
            return Exception("Generic injected error")

        def get_error_statistics(self) -> Dict[str, Any]:
            """Get error injection statistics."""
            return {
                'error_counts': self.error_counts.copy(),
                'active_configs': len(self.error_configs)
            }

    return ErrorInjectionService


# === SERVICE INTEGRATION MOCKS ===

@pytest.fixture
def enhanced_mock_services():
    """Enhanced mock services with realistic behavior simulation."""

    class EnhancedMockServices:
        def __init__(self):
            self.email_service = self._create_email_service_mock()
            self.notification_service = self._create_notification_service_mock()
            self.audit_service = self._create_audit_service_mock()

        def _create_email_service_mock(self):
            """Create enhanced email service mock."""
            mock = MagicMock()

            # Simulate email sending with realistic delays and failures
            async def send_email_simulation(*args, **kwargs):
                # Simulate network delay
                await asyncio.sleep(random.uniform(0.01, 0.1))

                # Simulate occasional failures
                if random.random() < 0.05:  # 5% failure rate
                    raise Exception("SMTP connection failed")

                return True

            mock.send_admin_permission_notification = AsyncMock(side_effect=send_email_simulation)
            mock.send_admin_security_alert = AsyncMock(side_effect=send_email_simulation)
            mock.send_admin_welcome_email = AsyncMock(side_effect=send_email_simulation)

            return mock

        def _create_notification_service_mock(self):
            """Create enhanced notification service mock."""
            mock = MagicMock()

            async def notification_simulation(*args, **kwargs):
                # Simulate processing delay
                await asyncio.sleep(random.uniform(0.005, 0.05))

                # Simulate rare failures
                if random.random() < 0.02:  # 2% failure rate
                    raise Exception("Notification service unavailable")

                return True

            mock.send_admin_notification = AsyncMock(side_effect=notification_simulation)
            mock.send_security_alert = AsyncMock(side_effect=notification_simulation)
            mock.send_bulk_notification = AsyncMock(side_effect=notification_simulation)

            return mock

        def _create_audit_service_mock(self):
            """Create enhanced audit service mock."""
            mock = MagicMock()

            async def audit_simulation(*args, **kwargs):
                # Simulate audit logging delay
                await asyncio.sleep(random.uniform(0.001, 0.01))
                return True

            mock.log_admin_activity = AsyncMock(side_effect=audit_simulation)
            mock.create_audit_entry = AsyncMock(side_effect=audit_simulation)

            return mock

    return EnhancedMockServices


# === CONCURRENT TESTING HELPERS ===

@pytest.fixture
def concurrency_controller():
    """Controller for managing concurrent test operations."""

    import asyncio
    import threading
    from concurrent.futures import ThreadPoolExecutor

    class ConcurrencyController:
        def __init__(self):
            self.active_tasks = {}
            self.completion_events = {}
            self.thread_pool = ThreadPoolExecutor(max_workers=10)

        async def run_concurrent_tasks(
            self,
            tasks: List[Callable],
            max_concurrency: int = 10,
            timeout: float = 30.0
        ) -> List[Any]:
            """Run tasks concurrently with controlled concurrency."""
            semaphore = asyncio.Semaphore(max_concurrency)

            async def limited_task(task_func):
                async with semaphore:
                    return await task_func()

            # Wrap tasks with semaphore
            limited_tasks = [limited_task(task) for task in tasks]

            # Execute with timeout
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*limited_tasks, return_exceptions=True),
                    timeout=timeout
                )
                return results
            except asyncio.TimeoutError:
                raise Exception(f"Concurrent tasks timed out after {timeout} seconds")

        def create_task_barrier(self, num_tasks: int) -> str:
            """Create a barrier for synchronizing concurrent tasks."""
            barrier_id = str(uuid.uuid4())
            self.completion_events[barrier_id] = {
                'event': asyncio.Event(),
                'completed_tasks': 0,
                'total_tasks': num_tasks
            }
            return barrier_id

        async def wait_at_barrier(self, barrier_id: str, task_id: str):
            """Wait at barrier until all tasks reach this point."""
            if barrier_id not in self.completion_events:
                raise ValueError(f"Barrier {barrier_id} not found")

            barrier_info = self.completion_events[barrier_id]
            barrier_info['completed_tasks'] += 1

            if barrier_info['completed_tasks'] >= barrier_info['total_tasks']:
                barrier_info['event'].set()
            else:
                await barrier_info['event'].wait()

        def cleanup_barrier(self, barrier_id: str):
            """Clean up barrier resources."""
            if barrier_id in self.completion_events:
                del self.completion_events[barrier_id]

    return ConcurrencyController


# === TEST DATA PERSISTENCE ===

@pytest.fixture
def test_data_manager(integration_db_session):
    """Manager for handling test data lifecycle."""

    class TestDataManager:
        def __init__(self, db_session: Session):
            self.db = db_session
            self.created_objects = []
            self.cleanup_functions = []

        def register_cleanup(self, cleanup_func: Callable):
            """Register a cleanup function."""
            self.cleanup_functions.append(cleanup_func)

        def add_test_object(self, obj: Any):
            """Register an object for cleanup."""
            self.created_objects.append(obj)
            self.db.add(obj)

        def commit_test_data(self):
            """Commit all test data."""
            try:
                self.db.commit()
                for obj in self.created_objects:
                    self.db.refresh(obj)
            except Exception as e:
                self.db.rollback()
                raise e

        def cleanup_all(self):
            """Clean up all test data."""
            # Run custom cleanup functions
            for cleanup_func in reversed(self.cleanup_functions):
                try:
                    cleanup_func()
                except Exception as e:
                    print(f"Cleanup function failed: {e}")

            # Remove created objects
            for obj in reversed(self.created_objects):
                try:
                    self.db.delete(obj)
                except Exception as e:
                    print(f"Failed to delete object: {e}")

            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                print(f"Failed to commit cleanup: {e}")

    manager = TestDataManager(integration_db_session)
    yield manager
    manager.cleanup_all()


# === REALISTIC DATA GENERATORS ===

@pytest.fixture
def realistic_data_generator():
    """Generator for realistic test data patterns."""

    class RealisticDataGenerator:
        @staticmethod
        def generate_email_addresses(count: int, domain: str = "mestore.com") -> List[str]:
            """Generate realistic email addresses."""
            first_names = ["Juan", "Maria", "Carlos", "Ana", "Luis", "Sofia", "Miguel", "Carmen"]
            last_names = ["Garcia", "Rodriguez", "Martinez", "Lopez", "Hernandez", "Gonzalez"]

            emails = []
            for i in range(count):
                first = random.choice(first_names).lower()
                last = random.choice(last_names).lower()
                number = random.randint(1, 999) if random.random() < 0.3 else ""
                email = f"{first}.{last}{number}@{domain}"
                emails.append(email)

            return emails

        @staticmethod
        def generate_colombian_departments() -> List[str]:
            """Generate Colombian departments for testing."""
            return [
                "Antioquia", "Atlántico", "Bogotá D.C.", "Bolívar", "Boyacá",
                "Caldas", "Caquetá", "Cauca", "César", "Chocó", "Córdoba",
                "Cundinamarca", "Guainía", "Guaviare", "Huila", "La Guajira",
                "Magdalena", "Meta", "Nariño", "Norte de Santander", "Putumayo",
                "Quindío", "Risaralda", "San Andrés y Providencia", "Santander",
                "Sucre", "Tolima", "Valle del Cauca", "Vaupés", "Vichada"
            ]

        @staticmethod
        def generate_user_activity_patterns() -> Dict[str, Any]:
            """Generate realistic user activity patterns."""
            # Business hours weighted activity
            business_hours = list(range(8, 18))  # 8 AM to 6 PM
            off_hours = list(range(0, 8)) + list(range(18, 24))

            return {
                'business_hours_weight': 0.8,
                'off_hours_weight': 0.2,
                'business_hours': business_hours,
                'off_hours': off_hours,
                'peak_hours': [10, 11, 14, 15, 16],  # 10-11 AM, 2-4 PM
                'weekend_activity_reduction': 0.3
            }

    return RealisticDataGenerator