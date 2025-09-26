# ~/app/services/admin_permission_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Admin Permission Service
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: admin_permission_service.py
# Ruta: ~/app/services/admin_permission_service.py
# Autor: Jairo - Backend Senior Developer
# Fecha de Creación: 2025-09-14
# Última Actualización: 2025-09-14
# Versión: 1.0.0
# Propósito: SUPERUSER Admin Panel - Permission Management Service
#
# TASK_002A: SUPERUSER Admin Panel Backend - Admin Management System
# - Granular permission validation and assignment
# - Role-based access control (RBAC) implementation
# - Permission inheritance and delegation
# - Security clearance level validation
#
# ---------------------------------------------------------------------------------------------

"""
SUPERUSER Admin Permission Management Service.

Este servicio implementa el sistema granular de permisos administrativos:
- Permission validation for admin operations
- Role-based access control with inheritance
- Security clearance level enforcement
- Permission delegation and temporary grants
- Audit logging for permission changes
- Cache optimization for permission checks
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import redis
import json
from app.core.config import settings
from app.models.user import User, UserType
from app.models.admin_permission import (
    AdminPermission,
    PermissionScope,
    PermissionAction,
    ResourceType,
    admin_user_permissions,
    SYSTEM_PERMISSIONS
)
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, ActionResult, RiskLevel
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)


class PermissionDeniedError(Exception):
    """Exception raised when permission is denied."""
    def __init__(self, message: str, required_permission: str = None, user_level: int = None):
        self.message = message
        self.required_permission = required_permission
        self.user_level = user_level
        super().__init__(self.message)


class InsufficientClearanceError(PermissionDeniedError):
    """Exception raised when user has insufficient security clearance."""
    pass


class AdminPermissionService:
    """
    Enterprise Admin Permission Management Service.

    Provides comprehensive permission management for SUPERUSER admin operations:
    - Granular permission validation
    - Role-based access control with inheritance
    - Security clearance level enforcement
    - Permission caching for performance
    - Audit logging for compliance
    """

    def __init__(self):
        """Initialize the permission service with Redis cache."""
        try:
            self.redis_client = redis.from_url(settings.REDIS_CACHE_URL)
            self.cache_ttl = settings.REDIS_CACHE_TTL
        except Exception as e:
            logger.warning(f"Redis not available for permission caching: {e}")
            self.redis_client = None
            self.cache_ttl = 0

        # Permission hierarchy for inheritance
        self.permission_hierarchy = {
            UserType.SYSTEM: 5,
            UserType.SUPERUSER: 4,
            UserType.ADMIN: 3,
            UserType.VENDOR: 2,
            UserType.BUYER: 1
        }

    # === CORE PERMISSION VALIDATION ===

    async def validate_permission(
        self,
        db: Session,
        user: User,
        resource_type: ResourceType,
        action: PermissionAction,
        scope: PermissionScope = PermissionScope.USER,
        target_user: User = None,
        additional_context: Dict[str, Any] = None
    ) -> bool:
        """
        Validate if user has permission for specific action.

        Args:
            db: Database session
            user: User attempting the action
            resource_type: Type of resource being accessed
            action: Action being performed
            scope: Scope of the action
            target_user: Target user for user management actions
            additional_context: Additional context for validation

        Returns:
            bool: True if permission granted, False otherwise

        Raises:
            PermissionDeniedError: If permission is explicitly denied
            InsufficientClearanceError: If user lacks required clearance
        """

        # Quick check for system users
        if user.user_type == UserType.SYSTEM:
            await self._log_permission_check(db, user, resource_type, action, scope, True, "SYSTEM_USER")
            return True

        # Build permission key
        permission_key = f"{resource_type.value}.{action.value}.{scope.value}".lower()

        # Check cache first
        cached_result = await self._get_cached_permission(user.id, permission_key)
        if cached_result is not None:
            await self._log_permission_check(db, user, resource_type, action, scope, cached_result, "CACHED")
            return cached_result

        # Validate base requirements
        if not await self._validate_base_requirements(db, user):
            await self._cache_permission_result(user.id, permission_key, False)
            raise PermissionDeniedError("User does not meet base security requirements")

        # Get required permission
        required_permission = await self._get_required_permission(db, resource_type, action, scope)

        if not required_permission:
            # No specific permission required - check user type hierarchy
            result = await self._validate_by_hierarchy(user, resource_type, action, scope)
        else:
            # Check specific permission
            result = await self._validate_specific_permission(db, user, required_permission, target_user)

        # Additional context validation
        if result and additional_context:
            result = await self._validate_additional_context(db, user, required_permission, additional_context)

        # Cache result
        await self._cache_permission_result(user.id, permission_key, result)

        # Log the permission check
        await self._log_permission_check(db, user, resource_type, action, scope, result)

        if not result:
            permission_name = required_permission.name if required_permission else permission_key
            raise PermissionDeniedError(
                f"Permission denied for {permission_name}",
                required_permission=permission_name,
                user_level=user.security_clearance_level
            )

        return result

    async def _validate_base_requirements(self, db: Session, user: User) -> bool:
        """Validate base security requirements for admin users with performance optimization."""

        # Performance optimization: Do all checks in memory without DB queries
        # Must be active and verified
        if not user.is_active or not user.is_verified:
            return False

        # Must be admin level or higher
        if not user.is_admin_or_higher():
            return False

        # Account must not be locked
        if user.is_account_locked():
            return False

        # Must have accepted compliance requirements
        if not user.has_required_colombian_consents():
            return False

        return True

    async def _get_required_permission(
        self,
        db: Session,
        resource_type: ResourceType,
        action: PermissionAction,
        scope: PermissionScope
    ) -> Optional[AdminPermission]:
        """Get the specific permission required for this action."""

        return db.query(AdminPermission).filter(
            AdminPermission.resource_type == resource_type,
            AdminPermission.action == action,
            AdminPermission.scope == scope
        ).first()

    async def _validate_by_hierarchy(
        self,
        user: User,
        resource_type: ResourceType,
        action: PermissionAction,
        scope: PermissionScope
    ) -> bool:
        """Validate permission based on user type hierarchy."""

        user_level = self.permission_hierarchy.get(user.user_type, 0)

        # SECURITY FIX: Stricter permission requirements
        required_levels = {
            (ResourceType.USERS, PermissionAction.CREATE): 4,  # Increased from 3
            (ResourceType.USERS, PermissionAction.MANAGE): 5,  # Increased from 4
            (ResourceType.VENDORS, PermissionAction.APPROVE): 4,  # Increased from 3
            (ResourceType.VENDORS, PermissionAction.MANAGE): 5,  # Increased from 4
            (ResourceType.SETTINGS, PermissionAction.CONFIGURE): 5,  # Unchanged - system only
            (ResourceType.AUDIT_LOGS, PermissionAction.READ): 4,  # Increased from 3
            (ResourceType.TRANSACTIONS, PermissionAction.AUDIT): 5,  # Increased from 4
            # SECURITY FIX: Additional high-risk operations
            (ResourceType.USERS, PermissionAction.DELETE): 5,
            (ResourceType.PERMISSIONS, PermissionAction.GRANT): 5,
            (ResourceType.PERMISSIONS, PermissionAction.REVOKE): 5,
        }

        # SECURITY FIX: More restrictive scope modifiers
        scope_modifiers = {
            PermissionScope.SYSTEM: 3,    # Increased from 2 - system requires highest clearance
            PermissionScope.GLOBAL: 2,    # Increased from 1
            PermissionScope.DEPARTMENT: 0,
            PermissionScope.TEAM: -1,
            PermissionScope.USER: -1,
            PermissionScope.READ_ONLY: -1  # Increased from -2 to be more restrictive
        }

        base_level = required_levels.get((resource_type, action), 3)  # Increased default from 2
        scope_modifier = scope_modifiers.get(scope, 0)
        required_level = base_level + scope_modifier

        # SECURITY FIX: Additional security clearance validation
        if user_level >= required_level:
            # Must also meet security clearance requirements
            min_clearance = self._get_minimum_clearance_for_operation(resource_type, action, scope)
            if user.security_clearance_level < min_clearance:
                return False
            return True

        return False

    async def _validate_specific_permission(
        self,
        db: Session,
        user: User,
        permission: AdminPermission,
        target_user: User = None
    ) -> bool:
        """Validate a specific permission against user's grants."""

        # Check security clearance level
        if user.security_clearance_level < permission.required_clearance_level:
            raise InsufficientClearanceError(
                f"Insufficient security clearance. Required: {permission.required_clearance_level}, "
                f"User has: {user.security_clearance_level}"
            )

        # Check if user has this permission directly assigned
        user_permission = db.query(admin_user_permissions).filter(
            admin_user_permissions.c.user_id == user.id,
            admin_user_permissions.c.permission_id == permission.id,
            admin_user_permissions.c.is_active == True,
            or_(
                admin_user_permissions.c.expires_at == None,
                admin_user_permissions.c.expires_at > datetime.utcnow()
            )
        ).first()

        if user_permission:
            return True

        # Check role-based inheritance
        if permission.is_inheritable:
            return await self._check_inherited_permissions(db, user, permission)

        return False

    async def _check_inherited_permissions(
        self,
        db: Session,
        user: User,
        permission: AdminPermission
    ) -> bool:
        """Check if user inherits permission through role hierarchy."""

        # SECURITY FIX: Strict permission inheritance validation
        # No automatic inheritance for system-level permissions
        if permission.scope == PermissionScope.SYSTEM:
            return False

        # SECURITY FIX: SUPERUSER inheritance limited by clearance level
        if user.user_type == UserType.SUPERUSER:
            # Must have sufficient security clearance
            if user.security_clearance_level < permission.required_clearance_level:
                return False

            # Only inherit non-system permissions that are explicitly marked as inheritable
            if permission.is_inheritable and permission.scope != PermissionScope.SYSTEM:
                # Additional validation for high-risk permissions
                if permission.required_clearance_level >= 4:  # High clearance permissions
                    # Check if user has specific department/team context
                    if not user.department_id and permission.scope == PermissionScope.DEPARTMENT:
                        return False
                return True

        # SECURITY FIX: ADMIN inheritance strictly limited
        if user.user_type == UserType.ADMIN:
            # Must have sufficient clearance and be inheritable
            if (user.security_clearance_level < permission.required_clearance_level or
                not permission.is_inheritable):
                return False

            # Only specific scopes with additional context validation
            if permission.scope in [PermissionScope.DEPARTMENT, PermissionScope.TEAM]:
                # Must be assigned to relevant department/team
                if not user.department_id:
                    return False
                return True

            # User scope permissions only for own department
            if permission.scope == PermissionScope.USER:
                return True

        return False

    async def _validate_additional_context(
        self,
        db: Session,
        user: User,
        permission: AdminPermission,
        context: Dict[str, Any]
    ) -> bool:
        """Validate additional context-specific requirements."""

        if not permission or not permission.conditions:
            return True

        conditions = permission.conditions

        # Time-based restrictions
        if 'allowed_hours' in conditions:
            current_hour = datetime.utcnow().hour
            if current_hour not in conditions['allowed_hours']:
                return False

        # IP-based restrictions
        if 'allowed_ips' in conditions and 'ip_address' in context:
            if context['ip_address'] not in conditions['allowed_ips']:
                return False

        # Department-based restrictions
        if 'allowed_departments' in conditions:
            if user.department_id not in conditions['allowed_departments']:
                return False

        return True

    # === PERMISSION MANAGEMENT ===

    async def grant_permission(
        self,
        db: Session,
        granter: User,
        target_user: User,
        permission: AdminPermission,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Grant a permission to a user."""

        # SECURITY FIX: Enhanced permission granting validation
        # Validate granter can grant this permission
        if not await self._can_user_grant_permission(db, granter, permission, target_user):
            raise PermissionDeniedError(
                "Insufficient privileges to grant this permission",
                required_permission=permission.name,
                user_level=granter.security_clearance_level
            )

        # Check if permission already exists
        existing = db.query(admin_user_permissions).filter(
            admin_user_permissions.c.user_id == target_user.id,
            admin_user_permissions.c.permission_id == permission.id,
            admin_user_permissions.c.is_active == True
        ).first()

        if existing:
            return True  # Already granted

        # Insert new permission grant
        db.execute(
            admin_user_permissions.insert().values(
                user_id=target_user.id,
                permission_id=permission.id,
                granted_by_id=granter.id,
                granted_at=datetime.utcnow(),
                expires_at=expires_at,
                is_active=True
            )
        )

        # Clear cache for this user
        await self._clear_user_permission_cache(target_user.id)

        # Log the permission grant
        await self._log_admin_activity(
            db, granter, AdminActionType.SECURITY, "grant_permission",
            f"Granted permission {permission.name} to {target_user.email}",
            target_type="user", target_id=str(target_user.id)
        )

        db.commit()
        return True

    async def revoke_permission(
        self,
        db: Session,
        revoker: User,
        target_user: User,
        permission: AdminPermission
    ) -> bool:
        """Revoke a permission from a user."""

        # Validate revoker can revoke this permission
        if not permission.can_be_granted_by_user(revoker):
            raise PermissionDeniedError("Insufficient privileges to revoke this permission")

        # Update permission to inactive
        db.execute(
            admin_user_permissions.update()
            .where(
                and_(
                    admin_user_permissions.c.user_id == target_user.id,
                    admin_user_permissions.c.permission_id == permission.id
                )
            )
            .values(is_active=False)
        )

        # Clear cache for this user
        await self._clear_user_permission_cache(target_user.id)

        # Log the permission revocation
        await self._log_admin_activity(
            db, revoker, AdminActionType.SECURITY, "revoke_permission",
            f"Revoked permission {permission.name} from {target_user.email}",
            target_type="user", target_id=str(target_user.id)
        )

        db.commit()
        return True

    async def get_user_permissions(
        self,
        db: Session,
        user: User,
        include_inherited: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all permissions for a user."""

        # Direct permissions
        direct_permissions = db.query(AdminPermission).join(
            admin_user_permissions,
            AdminPermission.id == admin_user_permissions.c.permission_id
        ).filter(
            admin_user_permissions.c.user_id == user.id,
            admin_user_permissions.c.is_active == True,
            or_(
                admin_user_permissions.c.expires_at == None,
                admin_user_permissions.c.expires_at > datetime.utcnow()
            )
        ).all()

        permissions = []

        for perm in direct_permissions:
            permissions.append({
                **perm.to_dict(),
                'source': 'DIRECT',
                'granted_at': None  # Would need to query association table for this
            })

        # Add inherited permissions if requested
        if include_inherited:
            inherited = await self._get_inherited_permissions(db, user)
            permissions.extend(inherited)

        return permissions

    async def _get_inherited_permissions(
        self,
        db: Session,
        user: User
    ) -> List[Dict[str, Any]]:
        """Get permissions inherited through role hierarchy."""

        inherited_permissions = []

        if user.user_type == UserType.SUPERUSER:
            # SUPERUSER inherits most permissions except SYSTEM scope
            system_perms = db.query(AdminPermission).filter(
                AdminPermission.scope != PermissionScope.SYSTEM,
                AdminPermission.is_inheritable == True
            ).all()

            for perm in system_perms:
                inherited_permissions.append({
                    **perm.to_dict(),
                    'source': 'INHERITED_SUPERUSER'
                })

        elif user.user_type == UserType.ADMIN:
            # ADMIN inherits department/team/user level permissions
            admin_perms = db.query(AdminPermission).filter(
                AdminPermission.scope.in_([
                    PermissionScope.DEPARTMENT,
                    PermissionScope.TEAM,
                    PermissionScope.USER,
                    PermissionScope.READ_ONLY
                ]),
                AdminPermission.is_inheritable == True
            ).all()

            for perm in admin_perms:
                inherited_permissions.append({
                    **perm.to_dict(),
                    'source': 'INHERITED_ADMIN'
                })

        return inherited_permissions

    # === SECURITY VALIDATION METHODS ===

    def _get_minimum_clearance_for_operation(
        self,
        resource_type: ResourceType,
        action: PermissionAction,
        scope: PermissionScope
    ) -> int:
        """Get minimum security clearance required for operation."""

        # Base clearance requirements
        base_clearance = {
            (ResourceType.USERS, PermissionAction.MANAGE): 4,
            (ResourceType.USERS, PermissionAction.DELETE): 5,
            (ResourceType.VENDORS, PermissionAction.MANAGE): 4,
            (ResourceType.SETTINGS, PermissionAction.CONFIGURE): 5,
            (ResourceType.AUDIT_LOGS, PermissionAction.READ): 3,
            (ResourceType.TRANSACTIONS, PermissionAction.AUDIT): 4,
            (ResourceType.PERMISSIONS, PermissionAction.GRANT): 5,
            (ResourceType.PERMISSIONS, PermissionAction.REVOKE): 5,
        }

        # Scope adjustments
        scope_adjustments = {
            PermissionScope.SYSTEM: 2,
            PermissionScope.GLOBAL: 1,
            PermissionScope.DEPARTMENT: 0,
            PermissionScope.TEAM: 0,
            PermissionScope.USER: 0,
            PermissionScope.READ_ONLY: -1
        }

        base = base_clearance.get((resource_type, action), 3)
        adjustment = scope_adjustments.get(scope, 0)

        return max(1, base + adjustment)

    async def _can_user_grant_permission(
        self,
        db: Session,
        granter: User,
        permission: AdminPermission,
        target_user: User
    ) -> bool:
        """Enhanced validation for permission granting."""

        # SECURITY FIX: Strict granting rules
        # 1. Granter must have higher or equal clearance than the permission requires
        if granter.security_clearance_level < permission.required_clearance_level:
            return False

        # 2. Cannot grant system-level permissions unless user is SYSTEM type
        if permission.scope == PermissionScope.SYSTEM and granter.user_type != UserType.SYSTEM:
            return False

        # 3. Cannot elevate user above granter's level
        if target_user.user_type == UserType.SYSTEM and granter.user_type != UserType.SYSTEM:
            return False

        # 4. Granter must have the permission themselves (direct or inherited)
        try:
            has_permission = await self.validate_permission(
                db, granter, permission.resource_type, permission.action, permission.scope
            )
            if not has_permission:
                return False
        except (PermissionDeniedError, InsufficientClearanceError):
            return False

        # 5. Additional context validation for department-scoped permissions
        if permission.scope == PermissionScope.DEPARTMENT:
            if not granter.department_id or not target_user.department_id:
                return False
            # Can only grant within same department unless SUPERUSER+
            if (granter.department_id != target_user.department_id and
                granter.user_type not in [UserType.SYSTEM, UserType.SUPERUSER]):
                return False

        return True

    # === CACHING METHODS ===

    async def _get_cached_permission(self, user_id: str, permission_key: str) -> Optional[bool]:
        """Get cached permission result with performance optimization."""
        if not self.redis_client:
            return None

        try:
            cache_key = f"permission:{user_id}:{permission_key}"
            # Use pipeline for better performance
            pipe = self.redis_client.pipeline()
            pipe.get(cache_key)
            results = pipe.execute()
            result = results[0]
            return json.loads(result) if result else None
        except Exception as e:
            logger.warning(f"Error reading permission cache: {e}")
            return None

    async def _cache_permission_result(self, user_id: str, permission_key: str, result: bool):
        """Cache permission result with performance optimization."""
        if not self.redis_client:
            return

        try:
            cache_key = f"permission:{user_id}:{permission_key}"
            # Use pipeline for better performance
            pipe = self.redis_client.pipeline()
            pipe.setex(cache_key, self.cache_ttl, json.dumps(result))
            pipe.execute()
        except Exception as e:
            logger.warning(f"Error caching permission result: {e}")

    async def _clear_user_permission_cache(self, user_id: str):
        """Clear all cached permissions for a user."""
        if not self.redis_client:
            return

        try:
            pattern = f"permission:{user_id}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.warning(f"Error clearing permission cache: {e}")

    # === LOGGING METHODS ===

    async def _log_permission_check(
        self,
        db: Session,
        user: User,
        resource_type: ResourceType,
        action: PermissionAction,
        scope: PermissionScope,
        result: bool,
        source: str = "VALIDATION"
    ):
        """Log permission check for audit purposes with performance optimization."""

        try:
            # Performance optimization: Skip logging for cached results to reduce DB load
            if source == "CACHED":
                return

            # Performance optimization: Only log failed attempts and critical operations
            if not result or scope == PermissionScope.SYSTEM:
                log_entry = AdminActivityLog(
                    admin_user_id=user.id,
                    admin_email=user.email,
                    admin_full_name=user.full_name,
                    action_type=AdminActionType.SECURITY,
                    action_name="permission_check",
                    action_description=f"Permission check: {resource_type.value}.{action.value}.{scope.value}",
                    result=ActionResult.SUCCESS if result else ActionResult.BLOCKED,
                    risk_level=RiskLevel.LOW,
                    custom_fields={
                        'resource_type': resource_type.value,
                        'action': action.value,
                        'scope': scope.value,
                        'source': source
                    }
                )

                db.add(log_entry)
                # Don't commit here - let the calling function handle it

        except Exception as e:
            logger.error(f"Error logging permission check: {e}")

    async def _log_admin_activity(
        self,
        db: Session,
        admin_user: User,
        action_type: AdminActionType,
        action_name: str,
        description: str,
        target_type: str = None,
        target_id: str = None,
        risk_level: RiskLevel = RiskLevel.MEDIUM
    ):
        """Log admin activity."""

        try:
            log_entry = AdminActivityLog(
                admin_user_id=admin_user.id,
                admin_email=admin_user.email,
                admin_full_name=admin_user.full_name,
                action_type=action_type,
                action_name=action_name,
                action_description=description,
                target_type=target_type,
                target_id=target_id,
                result=ActionResult.SUCCESS,
                risk_level=risk_level
            )

            db.add(log_entry)

        except Exception as e:
            logger.error(f"Error logging admin activity: {e}")

    # === INITIALIZATION METHODS ===

    async def initialize_system_permissions(self, db: Session):
        """Initialize system permissions from predefined list."""

        try:
            for perm_data in SYSTEM_PERMISSIONS:
                # Check if permission already exists
                existing = db.query(AdminPermission).filter(
                    AdminPermission.name == perm_data["name"]
                ).first()

                if not existing:
                    permission = AdminPermission(**perm_data)
                    db.add(permission)

            db.commit()
            logger.info("System permissions initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing system permissions: {e}")
            db.rollback()
            raise


# Global instance
admin_permission_service = AdminPermissionService()