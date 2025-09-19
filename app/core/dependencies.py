"""
Integrated Service Dependencies
===============================

Unified dependency injection system for all integrated Phase 2 components.
Provides service container, health checks, and lifecycle management for:
- Authentication services (secure and legacy)
- Payment services (Wompi, fraud detection, commissions)
- Performance services (monitoring, caching, optimization)
- Security services (middleware, audit, error handling)
- Logging services (structured logging, correlation)

This module ensures proper service initialization, dependency resolution,
and graceful lifecycle management for the entire integrated system.

Author: System Architect AI
Date: 2025-09-17
Purpose: Unified service container and dependency management
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional, Callable, TypeVar, Type
from dataclasses import dataclass
from datetime import datetime
import weakref

# Import all integrated services
from app.core.integrated_auth import integrated_auth_service
from app.services.integrated_payment_service import integrated_payment_service
from app.services.integrated_performance_service import integrated_performance_service
from app.core.unified_error_handler import unified_error_handler
from app.core.integrated_logging_system import integrated_logging_system
from app.core.system_integration_validator import system_integration_validator

# Import core services
from app.core.config import settings
from app.database import get_db
from app.core.redis.session import get_redis_sessions

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class ServiceInfo:
    """Service registration information"""
    name: str
    instance: Any
    initialized: bool = False
    health_check: Optional[Callable] = None
    cleanup: Optional[Callable] = None
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class ServiceContainer:
    """
    Unified service container for dependency injection and lifecycle management.
    """

    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.initialization_order: List[str] = []
        self._initialized = False
        self._shutdown_handlers: List[Callable] = []

    def register_service(
        self,
        name: str,
        instance: Any,
        health_check: Optional[Callable] = None,
        cleanup: Optional[Callable] = None,
        dependencies: List[str] = None
    ):
        """
        Register a service with the container.

        Args:
            name: Service name
            instance: Service instance
            health_check: Optional health check function
            cleanup: Optional cleanup function
            dependencies: List of service dependencies
        """
        self.services[name] = ServiceInfo(
            name=name,
            instance=instance,
            health_check=health_check,
            cleanup=cleanup,
            dependencies=dependencies or []
        )

        logger.debug(f"Registered service: {name}")

    def get_service(self, name: str) -> Any:
        """Get service instance by name"""
        service_info = self.services.get(name)
        if not service_info:
            raise ValueError(f"Service '{name}' not registered")

        if not service_info.initialized:
            logger.warning(f"Service '{name}' requested but not initialized")

        return service_info.instance

    async def initialize_all(self):
        """Initialize all registered services in dependency order"""
        if self._initialized:
            logger.warning("Service container already initialized")
            return

        logger.info("Initializing service container...")

        # Resolve dependency order
        self._resolve_initialization_order()

        # Initialize services in order
        for service_name in self.initialization_order:
            await self._initialize_service(service_name)

        self._initialized = True
        logger.info("Service container initialized successfully")

    async def cleanup(self):
        """Cleanup all services in reverse order"""
        if not self._initialized:
            return

        logger.info("Cleaning up service container...")

        # Run shutdown handlers
        for handler in self._shutdown_handlers:
            try:
                await handler()
            except Exception as e:
                logger.error(f"Error in shutdown handler: {str(e)}")

        # Cleanup services in reverse order
        for service_name in reversed(self.initialization_order):
            await self._cleanup_service(service_name)

        self._initialized = False
        logger.info("Service container cleanup completed")

    async def health_check_all(self) -> Dict[str, Any]:
        """Run health checks for all services"""
        health_results = {}

        for service_name, service_info in self.services.items():
            if service_info.health_check and service_info.initialized:
                try:
                    result = await service_info.health_check()
                    health_results[service_name] = result
                except Exception as e:
                    health_results[service_name] = {
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
            else:
                health_results[service_name] = {
                    "status": "not_initialized" if not service_info.initialized else "no_health_check",
                    "timestamp": datetime.utcnow().isoformat()
                }

        # Overall health
        unhealthy_count = sum(
            1 for result in health_results.values()
            if result.get("status") in ["unhealthy", "degraded"]
        )

        overall_status = "healthy" if unhealthy_count == 0 else (
            "degraded" if unhealthy_count <= len(health_results) // 2 else "unhealthy"
        )

        return {
            "overall_status": overall_status,
            "services": health_results,
            "total_services": len(self.services),
            "unhealthy_services": unhealthy_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    def add_shutdown_handler(self, handler: Callable):
        """Add shutdown handler"""
        self._shutdown_handlers.append(handler)

    def _resolve_initialization_order(self):
        """Resolve service initialization order based on dependencies"""
        visited = set()
        temp_visited = set()
        order = []

        def visit(service_name: str):
            if service_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {service_name}")

            if service_name in visited:
                return

            temp_visited.add(service_name)

            service_info = self.services.get(service_name)
            if service_info:
                for dependency in service_info.dependencies:
                    if dependency in self.services:
                        visit(dependency)

            temp_visited.remove(service_name)
            visited.add(service_name)
            order.append(service_name)

        for service_name in self.services.keys():
            visit(service_name)

        self.initialization_order = order

    async def _initialize_service(self, service_name: str):
        """Initialize individual service"""
        service_info = self.services.get(service_name)
        if not service_info or service_info.initialized:
            return

        try:
            logger.debug(f"Initializing service: {service_name}")

            # Call initialize method if available
            if hasattr(service_info.instance, 'initialize'):
                await service_info.instance.initialize()

            service_info.initialized = True
            logger.debug(f"Service initialized: {service_name}")

        except Exception as e:
            logger.error(f"Failed to initialize service {service_name}: {str(e)}")
            raise

    async def _cleanup_service(self, service_name: str):
        """Cleanup individual service"""
        service_info = self.services.get(service_name)
        if not service_info or not service_info.initialized:
            return

        try:
            logger.debug(f"Cleaning up service: {service_name}")

            if service_info.cleanup:
                await service_info.cleanup()

            service_info.initialized = False
            logger.debug(f"Service cleaned up: {service_name}")

        except Exception as e:
            logger.error(f"Error cleaning up service {service_name}: {str(e)}")


# Global service container instance
_service_container: Optional[ServiceContainer] = None


async def get_service_container() -> ServiceContainer:
    """Get or create the global service container"""
    global _service_container

    if _service_container is None:
        _service_container = ServiceContainer()

        # Register all integrated services
        await _register_integrated_services(_service_container)

        # Initialize container
        await _service_container.initialize_all()

    return _service_container


async def _register_integrated_services(container: ServiceContainer):
    """Register all integrated services with the container"""
    logger.info("Registering integrated services...")

    # Authentication Services
    container.register_service(
        name="integrated_auth",
        instance=integrated_auth_service,
        health_check=integrated_auth_service.health_check,
        dependencies=[]  # Base service
    )

    # Payment Services
    container.register_service(
        name="integrated_payment",
        instance=integrated_payment_service,
        health_check=integrated_payment_service.health_check,
        dependencies=["integrated_auth"]  # Depends on auth for user context
    )

    # Performance Services
    container.register_service(
        name="integrated_performance",
        instance=integrated_performance_service,
        health_check=integrated_performance_service.health_check,
        dependencies=[]  # Independent service
    )

    # Error Handling Services
    container.register_service(
        name="unified_error_handler",
        instance=unified_error_handler,
        health_check=unified_error_handler.health_check,
        dependencies=[]  # Base service
    )

    # Logging Services
    container.register_service(
        name="integrated_logging",
        instance=integrated_logging_system,
        health_check=integrated_logging_system.health_check,
        dependencies=[]  # Base service
    )

    # System Validator (for operational monitoring)
    container.register_service(
        name="system_validator",
        instance=system_integration_validator,
        dependencies=["integrated_auth", "integrated_payment", "integrated_performance",
                     "unified_error_handler", "integrated_logging"]
    )

    logger.info("All integrated services registered")


# Dependency injection functions for FastAPI

async def get_integrated_auth_service():
    """Get integrated authentication service"""
    container = await get_service_container()
    return container.get_service("integrated_auth")


async def get_integrated_payment_service():
    """Get integrated payment service"""
    container = await get_service_container()
    return container.get_service("integrated_payment")


async def get_integrated_performance_service():
    """Get integrated performance service"""
    container = await get_service_container()
    return container.get_service("integrated_performance")


async def get_unified_error_handler():
    """Get unified error handler"""
    container = await get_service_container()
    return container.get_service("unified_error_handler")


async def get_integrated_logging_system():
    """Get integrated logging system"""
    container = await get_service_container()
    return container.get_service("integrated_logging")


async def get_system_validator():
    """Get system integration validator"""
    container = await get_service_container()
    return container.get_service("system_validator")


# Health check dependencies

async def get_health_check_services() -> Dict[str, Any]:
    """Get health status for all services"""
    try:
        container = await get_service_container()
        return await container.health_check_all()
    except Exception as e:
        logger.error(f"Failed to get health check services: {str(e)}")
        return {
            "overall_status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Application lifespan management

@asynccontextmanager
async def service_lifespan(app):
    """Application lifespan context manager with service container"""
    logger.info("Starting application with integrated services...")

    try:
        # Initialize service container
        container = await get_service_container()

        # Add application to container for access
        container.register_service("fastapi_app", app)

        logger.info("Application started successfully with all services")
        yield

    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    finally:
        # Cleanup services
        if _service_container:
            await _service_container.cleanup()
        logger.info("Application shutdown completed")


# Service health monitoring

async def monitor_service_health():
    """Background task to monitor service health"""
    while True:
        try:
            health_data = await get_health_check_services()

            if health_data.get("overall_status") == "unhealthy":
                logger.warning(f"System health degraded: {health_data.get('unhealthy_services', 0)} services unhealthy")

            # Log health status
            container = await get_service_container()
            logging_service = container.get_service("integrated_logging")

            if logging_service:
                context = logging_service.create_correlation_context(operation="health_monitoring")
                await logging_service.log_system_event(
                    event_type="health_check",
                    message=f"System health: {health_data.get('overall_status')}",
                    context=context,
                    system_data=health_data
                )

            # Wait before next check
            await asyncio.sleep(300)  # 5 minutes

        except Exception as e:
            logger.error(f"Error in health monitoring: {str(e)}")
            await asyncio.sleep(60)  # Wait 1 minute on error


# Utility functions

async def validate_system_integration(include_load_tests: bool = False) -> Dict[str, Any]:
    """Run system integration validation"""
    try:
        validator = await get_system_validator()
        report = await validator.run_complete_validation(
            include_performance_tests=True,
            include_load_tests=include_load_tests
        )

        return {
            "validation_report": {
                "overall_status": report.overall_status.value,
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "critical_failures": report.critical_failures,
                "validation_time": report.validation_time,
                "recommendations": report.recommendations
            },
            "detailed_results": [
                {
                    "test_name": result.test_name,
                    "status": result.status.value,
                    "criticality": result.criticality.value,
                    "message": result.message,
                    "duration_ms": result.duration_ms,
                    "error": result.error
                }
                for result in report.results
            ]
        }

    except Exception as e:
        logger.error(f"System validation failed: {str(e)}")
        return {
            "validation_report": {
                "overall_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        }