# ~/app/models/admin_permission.py
# ---------------------------------------------------------------------------------------------
# MeStore - Admin Permission Model
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: admin_permission.py
# Ruta: ~/app/models/admin_permission.py
# Autor: Jairo - Backend Senior Developer
# Fecha de Creación: 2025-09-14
# Última Actualización: 2025-09-14
# Versión: 1.0.0
# Propósito: SUPERUSER Admin Panel - Granular Permission Management System
#
# TASK_002A: SUPERUSER Admin Panel Backend - Enhanced Database Models
# - Granular permission system for admin operations
# - Role-based access control expansion
# - Admin activity monitoring capabilities
# - Permission matrix management
#
# ---------------------------------------------------------------------------------------------

"""
SUPERUSER Admin Permission Management System.

Este módulo implementa el sistema granular de permisos para administradores:
- Granular permission assignment per admin operation
- Role-based permission inheritance
- Permission validation for critical operations
- Audit trail for permission changes
- Security clearance level validation
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy import Index, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from enum import Enum as PyEnum
import uuid

from app.models.base import BaseModel


class PermissionScope(str, PyEnum):
    """
    Enterprise Permission Scope Hierarchy.

    Defines the operational scope for each permission:
        SYSTEM: Full system access (SUPERUSER only)
        GLOBAL: Cross-company operations (SUPERUSER/HIGH-LEVEL ADMIN)
        DEPARTMENT: Department-wide operations (ADMIN)
        TEAM: Team-level operations (ADMIN)
        USER: Individual user operations (ADMIN/VENDOR)
        READ_ONLY: View-only access (OBSERVER roles)
    """
    SYSTEM = "SYSTEM"
    GLOBAL = "GLOBAL"
    DEPARTMENT = "DEPARTMENT"
    TEAM = "TEAM"
    USER = "USER"
    READ_ONLY = "READ_ONLY"


class PermissionAction(str, PyEnum):
    """
    Enterprise Admin Actions with granular control.

    Comprehensive list of admin operations for RBAC:
        CREATE: Create new resources
        READ: View/read resources
        UPDATE: Modify existing resources
        DELETE: Remove resources
        APPROVE: Approve workflows (vendor applications, etc.)
        REJECT: Reject workflows
        MANAGE: Full management permissions
        AUDIT: Access audit logs and reports
        EXPORT: Export data and reports
        IMPORT: Import data
        CONFIGURE: System configuration changes
        MONITOR: Real-time monitoring access
    """
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MANAGE = "MANAGE"
    AUDIT = "AUDIT"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    CONFIGURE = "CONFIGURE"
    MONITOR = "MONITOR"


class ResourceType(str, PyEnum):
    """
    Enterprise Resource Types for permission management.

    All manageable resources in the system:
        USERS: User management operations
        VENDORS: Vendor lifecycle management
        ORDERS: Order processing and management
        PRODUCTS: Product catalog management
        INVENTORY: Inventory operations
        TRANSACTIONS: Financial transaction management
        COMMISSIONS: Commission system management
        REPORTS: Business intelligence and reporting
        SETTINGS: System configuration
        AUDIT_LOGS: Audit trail management
        NOTIFICATIONS: Notification system
        PAYMENTS: Payment gateway management
        STORAGE: Storage location management
        ANALYTICS: Business analytics access
    """
    USERS = "USERS"
    VENDORS = "VENDORS"
    ORDERS = "ORDERS"
    PRODUCTS = "PRODUCTS"
    INVENTORY = "INVENTORY"
    TRANSACTIONS = "TRANSACTIONS"
    COMMISSIONS = "COMMISSIONS"
    REPORTS = "REPORTS"
    SETTINGS = "SETTINGS"
    AUDIT_LOGS = "AUDIT_LOGS"
    NOTIFICATIONS = "NOTIFICATIONS"
    PAYMENTS = "PAYMENTS"
    STORAGE = "STORAGE"
    ANALYTICS = "ANALYTICS"


# Association table for many-to-many relationship between users and permissions
admin_user_permissions = Table(
    'admin_user_permissions',
    BaseModel.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('admin_permissions.id'), primary_key=True),
    Column('granted_by_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Column('granted_at', DateTime(timezone=True), server_default=func.now()),
    Column('expires_at', DateTime(timezone=True), nullable=True),
    Column('is_active', Boolean, default=True, nullable=False),
    Index('ix_admin_user_permissions_user_active', 'user_id', 'is_active'),
    Index('ix_admin_user_permissions_granted_at', 'granted_at'),
)


class AdminPermission(BaseModel):
    """
    Enterprise Admin Permission Model.

    Granular permission system for SUPERUSER admin operations:
    - Fine-grained permission control per resource and action
    - Scope-based access control (SYSTEM/GLOBAL/DEPARTMENT/etc.)
    - Security clearance level validation
    - Permission inheritance and role-based assignment
    - Audit trail for permission changes
    - Expiration support for temporary permissions
    """

    __tablename__ = "admin_permissions"

    # === PRIMARY KEY ===
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Unique permission identifier"
    )

    # === PERMISSION DEFINITION ===
    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique permission name (e.g., 'users.create.global')"
    )

    display_name = Column(
        String(200),
        nullable=False,
        comment="Human-readable permission name"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Detailed description of what this permission allows"
    )

    # === PERMISSION CLASSIFICATION ===
    resource_type = Column(
        SQLEnum(ResourceType),
        nullable=False,
        comment="Resource type this permission applies to"
    )

    action = Column(
        SQLEnum(PermissionAction),
        nullable=False,
        comment="Action this permission allows"
    )

    scope = Column(
        SQLEnum(PermissionScope),
        nullable=False,
        comment="Operational scope of this permission"
    )

    # === SECURITY REQUIREMENTS ===
    required_clearance_level = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Minimum security clearance level required (1-5)"
    )

    requires_mfa = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this permission requires MFA verification"
    )

    requires_approval = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether actions with this permission require additional approval"
    )

    # === PERMISSION ATTRIBUTES ===
    is_system_permission = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is a critical system permission"
    )

    is_inheritable = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether this permission can be inherited through role hierarchy"
    )

    is_delegatable = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this permission can be delegated to other admins"
    )

    # === PERMISSION CONDITIONS ===
    conditions = Column(
        JSON,
        nullable=True,
        comment="Additional conditions for permission validation (JSON format)"
    )

    restrictions = Column(
        JSON,
        nullable=True,
        comment="Restrictions on permission usage (time-based, IP-based, etc.)"
    )

    # === PERMISSION METADATA ===
    category = Column(
        String(50),
        nullable=True,
        comment="Permission category for grouping and organization"
    )

    tags = Column(
        JSON,
        nullable=True,
        comment="Tags for permission classification and filtering"
    )

    risk_level = Column(
        String(20),
        default="MEDIUM",
        nullable=False,
        comment="Risk level: LOW, MEDIUM, HIGH, CRITICAL"
    )

    # === AUDIT AND COMPLIANCE ===
    compliance_requirements = Column(
        JSON,
        nullable=True,
        comment="Compliance requirements this permission must meet"
    )

    audit_required = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether usage of this permission must be audited"
    )

    # === RELATIONSHIPS ===
    # Many-to-many relationship with users through association table
    assigned_users = relationship(
        "User",
        secondary=admin_user_permissions,
        primaryjoin="AdminPermission.id == admin_user_permissions.c.permission_id",
        secondaryjoin="User.id == admin_user_permissions.c.user_id",
        lazy="select"
    )

    # === VALIDATION AND CONSTRAINTS ===
    __table_args__ = (
        UniqueConstraint('resource_type', 'action', 'scope', name='uq_permission_definition'),
        Index('ix_admin_permission_resource_action', 'resource_type', 'action'),
        Index('ix_admin_permission_scope_clearance', 'scope', 'required_clearance_level'),
        Index('ix_admin_permission_system_critical', 'is_system_permission', 'risk_level'),
        Index('ix_admin_permission_category', 'category'),
    )

    @validates('required_clearance_level')
    def validate_clearance_level(self, key, value):
        """Validate security clearance level is within valid range."""
        if not 1 <= value <= 5:
            raise ValueError("Security clearance level must be between 1 and 5")
        return value

    @validates('risk_level')
    def validate_risk_level(self, key, value):
        """Validate risk level is one of the allowed values."""
        allowed_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        if value not in allowed_levels:
            raise ValueError(f"Risk level must be one of: {allowed_levels}")
        return value

    @validates('name')
    def validate_permission_name(self, key, value):
        """Validate permission name follows naming convention."""
        if not value or len(value.strip()) < 3:
            raise ValueError("Permission name must be at least 3 characters long")

        # Convention: resource.action.scope (e.g., users.create.global)
        parts = value.lower().split('.')
        if len(parts) < 3:
            raise ValueError("Permission name should follow format: resource.action.scope")

        return value.lower()

    # === BUSINESS LOGIC METHODS ===

    def is_compatible_with_user_level(self, user_security_level: int) -> bool:
        """Check if permission is compatible with user's security clearance level."""
        return user_security_level >= self.required_clearance_level

    def can_be_granted_by_user(self, granter_user) -> bool:
        """Check if a user can grant this permission to others."""
        # Only SUPERUSER or users with higher clearance can grant permissions
        if not granter_user.is_superuser():
            return False

        # Must have higher clearance level than the permission requires
        return granter_user.security_clearance_level > self.required_clearance_level

    def requires_additional_validation(self) -> bool:
        """Check if permission requires additional validation steps."""
        return (
            self.requires_mfa or
            self.requires_approval or
            self.risk_level in ["HIGH", "CRITICAL"] or
            self.is_system_permission
        )

    def get_permission_key(self) -> str:
        """Generate standardized permission key for caching and validation."""
        return f"{self.resource_type.value}.{self.action.value}.{self.scope.value}".lower()

    def to_dict(self) -> Dict[str, Any]:
        """Convert permission to dictionary for API responses."""
        return {
            'id': str(self.id),
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'resource_type': self.resource_type.value,
            'action': self.action.value,
            'scope': self.scope.value,
            'required_clearance_level': self.required_clearance_level,
            'requires_mfa': self.requires_mfa,
            'requires_approval': self.requires_approval,
            'is_system_permission': self.is_system_permission,
            'is_inheritable': self.is_inheritable,
            'is_delegatable': self.is_delegatable,
            'category': self.category,
            'risk_level': self.risk_level,
            'audit_required': self.audit_required,
            'conditions': self.conditions,
            'restrictions': self.restrictions,
            'tags': self.tags,
            'compliance_requirements': self.compliance_requirements,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<AdminPermission(name='{self.name}', scope={self.scope.value}, level={self.required_clearance_level})>"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.display_name} ({self.scope.value})"


# Pre-defined system permissions for enterprise operations
SYSTEM_PERMISSIONS = [
    # User Management Permissions
    {
        "name": "users.create.global",
        "display_name": "Create Users (Global)",
        "description": "Create new users across all departments and roles",
        "resource_type": ResourceType.USERS,
        "action": PermissionAction.CREATE,
        "scope": PermissionScope.GLOBAL,
        "required_clearance_level": 4,
        "risk_level": "HIGH",
        "category": "User Management"
    },
    {
        "name": "users.manage.system",
        "display_name": "Manage System Users",
        "description": "Full management of system-level users and administrators",
        "resource_type": ResourceType.USERS,
        "action": PermissionAction.MANAGE,
        "scope": PermissionScope.SYSTEM,
        "required_clearance_level": 5,
        "risk_level": "CRITICAL",
        "is_system_permission": True,
        "requires_mfa": True,
        "category": "System Administration"
    },

    # Vendor Management Permissions
    {
        "name": "vendors.approve.global",
        "display_name": "Approve Vendor Applications",
        "description": "Approve or reject vendor applications system-wide",
        "resource_type": ResourceType.VENDORS,
        "action": PermissionAction.APPROVE,
        "scope": PermissionScope.GLOBAL,
        "required_clearance_level": 3,
        "risk_level": "MEDIUM",
        "category": "Vendor Management"
    },
    {
        "name": "vendors.manage.global",
        "display_name": "Manage Vendors (Global)",
        "description": "Full vendor lifecycle management across the platform",
        "resource_type": ResourceType.VENDORS,
        "action": PermissionAction.MANAGE,
        "scope": PermissionScope.GLOBAL,
        "required_clearance_level": 4,
        "risk_level": "HIGH",
        "category": "Vendor Management"
    },

    # Financial Operations Permissions
    {
        "name": "transactions.audit.global",
        "display_name": "Audit Financial Transactions",
        "description": "Access and audit all financial transactions and reports",
        "resource_type": ResourceType.TRANSACTIONS,
        "action": PermissionAction.AUDIT,
        "scope": PermissionScope.GLOBAL,
        "required_clearance_level": 4,
        "risk_level": "HIGH",
        "requires_mfa": True,
        "category": "Financial Operations"
    },
    {
        "name": "commissions.manage.global",
        "display_name": "Manage Commission System",
        "description": "Full management of commission calculations and payouts",
        "resource_type": ResourceType.COMMISSIONS,
        "action": PermissionAction.MANAGE,
        "scope": PermissionScope.GLOBAL,
        "required_clearance_level": 4,
        "risk_level": "HIGH",
        "category": "Financial Operations"
    },

    # System Configuration Permissions
    {
        "name": "settings.configure.system",
        "display_name": "Configure System Settings",
        "description": "Modify critical system configuration and parameters",
        "resource_type": ResourceType.SETTINGS,
        "action": PermissionAction.CONFIGURE,
        "scope": PermissionScope.SYSTEM,
        "required_clearance_level": 5,
        "risk_level": "CRITICAL",
        "is_system_permission": True,
        "requires_mfa": True,
        "requires_approval": True,
        "category": "System Administration"
    },

    # Analytics and Reporting Permissions
    {
        "name": "analytics.read.global",
        "display_name": "Access Global Analytics",
        "description": "View comprehensive business analytics and intelligence reports",
        "resource_type": ResourceType.ANALYTICS,
        "action": PermissionAction.READ,
        "scope": PermissionScope.GLOBAL,
        "required_clearance_level": 3,
        "risk_level": "MEDIUM",
        "category": "Analytics"
    },
    {
        "name": "reports.export.global",
        "display_name": "Export Global Reports",
        "description": "Export sensitive business reports and data",
        "resource_type": ResourceType.REPORTS,
        "action": PermissionAction.EXPORT,
        "scope": PermissionScope.GLOBAL,
        "required_clearance_level": 4,
        "risk_level": "HIGH",
        "requires_mfa": True,
        "category": "Reporting"
    }
]