# ~/app/api/v1/endpoints/admin_management.py
# ---------------------------------------------------------------------------------------------
# MeStore - SUPERUSER Admin Management APIs
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: admin_management.py
# Ruta: ~/app/api/v1/endpoints/admin_management.py
# Autor: Jairo - Backend Senior Developer
# Fecha de Creación: 2025-09-14
# Última Actualización: 2025-09-14
# Versión: 1.0.0
# Propósito: SUPERUSER Admin Panel - Admin Management System APIs
#
# TASK_002A: SUPERUSER Admin Panel Backend - Admin Management APIs
# - Create/manage administrators with granular permissions
# - Role-based access control expansion
# - Admin activity monitoring APIs
# - Permission matrix management endpoints
#
# ---------------------------------------------------------------------------------------------

"""
SUPERUSER Admin Management System APIs.

Este módulo implementa las APIs para gestión de administradores:
- Admin user creation and management
- Permission assignment and revocation
- Role-based access control (RBAC)
- Admin activity monitoring and audit
- Security clearance level management
- Bulk admin operations
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from pydantic import BaseModel, Field, EmailStr

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserType, VendorStatus
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType, admin_user_permissions
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, ActionResult, RiskLevel
from app.services.admin_permission_service import admin_permission_service, PermissionDeniedError
from app.schemas.user import UserResponse, UserCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


# === PYDANTIC SCHEMAS ===

class AdminCreateRequest(BaseModel):
    """Schema for creating new admin users."""
    email: EmailStr = Field(..., description="Admin email address")
    nombre: str = Field(..., min_length=2, max_length=100, description="First name")
    apellido: str = Field(..., min_length=2, max_length=100, description="Last name")
    user_type: UserType = Field(UserType.ADMIN, description="Admin user type")
    security_clearance_level: int = Field(3, ge=1, le=5, description="Security clearance level (1-5)")
    department_id: Optional[str] = Field(None, description="Department ID")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    telefono: Optional[str] = Field(None, description="Phone number")
    ciudad: Optional[str] = Field(None, description="City")
    departamento: Optional[str] = Field(None, description="Colombian department")
    initial_permissions: Optional[List[str]] = Field([], description="Initial permission names to grant")
    force_password_change: bool = Field(True, description="Force password change on first login")


class AdminUpdateRequest(BaseModel):
    """Schema for updating admin users."""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None
    security_clearance_level: Optional[int] = Field(None, ge=1, le=5)
    department_id: Optional[str] = None
    employee_id: Optional[str] = None
    performance_score: Optional[int] = Field(None, ge=0, le=100)
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None


class PermissionGrantRequest(BaseModel):
    """Schema for granting permissions."""
    permission_ids: List[str] = Field(..., description="List of permission IDs to grant")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp for permissions")
    reason: str = Field(..., min_length=10, description="Reason for granting permissions")


class PermissionRevokeRequest(BaseModel):
    """Schema for revoking permissions."""
    permission_ids: List[str] = Field(..., description="List of permission IDs to revoke")
    reason: str = Field(..., min_length=10, description="Reason for revoking permissions")


class BulkUserActionRequest(BaseModel):
    """Schema for bulk user actions."""
    user_ids: List[str] = Field(..., min_items=1, max_items=100, description="List of user IDs")
    action: str = Field(..., description="Action to perform: activate, deactivate, lock, unlock")
    reason: str = Field(..., min_length=10, description="Reason for bulk action")


class AdminResponse(BaseModel):
    """Enhanced admin user response with admin-specific fields."""
    id: str
    email: str
    nombre: Optional[str]
    apellido: Optional[str]
    full_name: str
    user_type: str
    is_active: bool
    is_verified: bool
    security_clearance_level: int
    department_id: Optional[str]
    employee_id: Optional[str]
    performance_score: int
    failed_login_attempts: int
    account_locked: bool
    requires_password_change: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    permission_count: Optional[int] = None
    last_activity: Optional[datetime] = None


# === ADMIN USER MANAGEMENT ENDPOINTS ===

@router.get("/admins", response_model=List[AdminResponse], summary="List Admin Users")
async def list_admin_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    user_type: Optional[UserType] = Query(None, description="Filter by user type"),
    department_id: Optional[str] = Query(None, description="Filter by department"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or email")
):
    """
    List admin users with filtering and pagination.

    **Required Permission:** users.read.global
    **Security Level:** 3+
    **Risk Level:** MEDIUM
    """

    # Validate permission
    await admin_permission_service.validate_permission(
        db, current_user,
        ResourceType.USERS, PermissionAction.READ, PermissionScope.GLOBAL
    )

    # Build query for admin users
    query = db.query(User).filter(
        User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
    )

    # Apply filters
    if user_type:
        query = query.filter(User.user_type == user_type)
    if department_id:
        query = query.filter(User.department_id == department_id)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(search_term),
                User.nombre.ilike(search_term),
                User.apellido.ilike(search_term)
            )
        )

    # Get total count for pagination
    total = query.count()

    # Apply pagination and ordering
    admins = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()

    # Convert to response format with additional admin data
    admin_responses = []
    for admin in admins:
        # Get permission count
        permission_count = db.query(func.count()).select_from(
            admin_user_permissions
        ).filter(
            admin_user_permissions.c.user_id == admin.id,
            admin_user_permissions.c.is_active == True
        ).scalar()

        # Get last activity
        last_activity = db.query(AdminActivityLog.created_at).filter(
            AdminActivityLog.admin_user_id == admin.id
        ).order_by(desc(AdminActivityLog.created_at)).first()

        admin_dict = admin.to_enterprise_dict()
        admin_dict.update({
            'permission_count': permission_count,
            'last_activity': last_activity[0] if last_activity else None
        })

        admin_responses.append(AdminResponse(**admin_dict))

    # Log the operation
    await admin_permission_service._log_admin_activity(
        db, current_user, AdminActionType.USER_MANAGEMENT, "list_admins",
        f"Listed {len(admin_responses)} admin users with filters: type={user_type}, dept={department_id}"
    )

    db.commit()

    return admin_responses


@router.post("/admins", response_model=AdminResponse, summary="Create Admin User")
async def create_admin_user(
    request: AdminCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new admin user with specified permissions.

    **Required Permission:** users.create.global
    **Security Level:** 4+
    **Risk Level:** HIGH
    """

    # Validate permission
    await admin_permission_service.validate_permission(
        db, current_user,
        ResourceType.USERS, PermissionAction.CREATE, PermissionScope.GLOBAL
    )

    # Additional validation for creating high-level admins
    if request.user_type == UserType.SUPERUSER:
        if not current_user.is_superuser():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only SUPERUSERs can create other SUPERUSERs"
            )

    # Validate security clearance level
    if request.security_clearance_level >= current_user.security_clearance_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create admin with equal or higher security clearance level"
        )

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # Create new admin user
    from app.services.auth_service import auth_service

    # Generate temporary password
    temp_password = auth_service.generate_secure_password()

    admin_data = {
        'email': request.email,
        'password_hash': auth_service.get_password_hash(temp_password),
        'nombre': request.nombre,
        'apellido': request.apellido,
        'user_type': request.user_type,
        'security_clearance_level': request.security_clearance_level,
        'department_id': request.department_id,
        'employee_id': request.employee_id,
        'telefono': request.telefono,
        'ciudad': request.ciudad,
        'departamento': request.departamento,
        'is_active': True,
        'is_verified': True,  # Admin users are pre-verified
        'force_password_change': request.force_password_change,
        'performance_score': 100,  # Start with perfect score
        'habeas_data_accepted': True,
        'data_processing_consent': True
    }

    new_admin = User(**admin_data)
    db.add(new_admin)
    db.flush()  # Get the ID

    # Grant initial permissions if specified
    if request.initial_permissions:
        for permission_name in request.initial_permissions:
            permission = db.query(AdminPermission).filter(
                AdminPermission.name == permission_name
            ).first()

            if permission:
                await admin_permission_service.grant_permission(
                    db, current_user, new_admin, permission
                )

    # Log the creation
    await admin_permission_service._log_admin_activity(
        db, current_user, AdminActionType.USER_MANAGEMENT, "create_admin",
        f"Created new admin user: {new_admin.email} (Type: {request.user_type.value})",
        target_type="user", target_id=str(new_admin.id),
        risk_level=RiskLevel.HIGH
    )

    db.commit()

    # TODO: Send welcome email with temporary password
    logger.info(f"New admin created: {new_admin.email}, temp password: {temp_password}")

    # Return response
    admin_dict = new_admin.to_enterprise_dict()
    admin_dict['permission_count'] = len(request.initial_permissions)
    admin_dict['last_activity'] = None

    return AdminResponse(**admin_dict)


@router.get("/admins/{admin_id}", response_model=AdminResponse, summary="Get Admin User Details")
async def get_admin_user(
    admin_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific admin user.

    **Required Permission:** users.read.global
    **Security Level:** 3+
    **Risk Level:** MEDIUM
    """

    # Validate permission
    await admin_permission_service.validate_permission(
        db, current_user,
        ResourceType.USERS, PermissionAction.READ, PermissionScope.GLOBAL
    )

    # Get the admin user
    admin = db.query(User).filter(
        User.id == admin_id,
        User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
    ).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )

    # Get additional admin data
    permission_count = db.query(func.count()).select_from(
        admin_user_permissions
    ).filter(
        admin_user_permissions.c.user_id == admin.id,
        admin_user_permissions.c.is_active == True
    ).scalar()

    last_activity = db.query(AdminActivityLog.created_at).filter(
        AdminActivityLog.admin_user_id == admin.id
    ).order_by(desc(AdminActivityLog.created_at)).first()

    # Log the access
    await admin_permission_service._log_admin_activity(
        db, current_user, AdminActionType.USER_MANAGEMENT, "get_admin",
        f"Retrieved admin user details: {admin.email}",
        target_type="user", target_id=str(admin.id)
    )

    db.commit()

    # Return response
    admin_dict = admin.to_enterprise_dict()
    admin_dict.update({
        'permission_count': permission_count,
        'last_activity': last_activity[0] if last_activity else None
    })

    return AdminResponse(**admin_dict)


@router.put("/admins/{admin_id}", response_model=AdminResponse, summary="Update Admin User")
async def update_admin_user(
    admin_id: str,
    request: AdminUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update admin user information.

    **Required Permission:** users.update.global
    **Security Level:** 3+
    **Risk Level:** MEDIUM
    """

    # Validate permission
    await admin_permission_service.validate_permission(
        db, current_user,
        ResourceType.USERS, PermissionAction.UPDATE, PermissionScope.GLOBAL
    )

    # Get the admin user
    admin = db.query(User).filter(
        User.id == admin_id,
        User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
    ).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )

    # Validate security clearance changes
    if (request.security_clearance_level and
        request.security_clearance_level >= current_user.security_clearance_level):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot set security clearance equal to or higher than your own"
        )

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(admin, field, value)

    # Log the update
    await admin_permission_service._log_admin_activity(
        db, current_user, AdminActionType.USER_MANAGEMENT, "update_admin",
        f"Updated admin user: {admin.email}, fields: {list(update_data.keys())}",
        target_type="user", target_id=str(admin.id)
    )

    db.commit()

    # Return response
    admin_dict = admin.to_enterprise_dict()
    admin_dict['permission_count'] = None  # Could query this if needed
    admin_dict['last_activity'] = None

    return AdminResponse(**admin_dict)


# === PERMISSION MANAGEMENT ENDPOINTS ===

@router.get("/admins/{admin_id}/permissions", summary="Get Admin Permissions")
async def get_admin_permissions(
    admin_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    include_inherited: bool = Query(True, description="Include inherited permissions")
):
    """
    Get all permissions for an admin user.

    **Required Permission:** users.read.global
    **Security Level:** 3+
    **Risk Level:** MEDIUM
    """

    # Validate permission
    await admin_permission_service.validate_permission(
        db, current_user,
        ResourceType.USERS, PermissionAction.READ, PermissionScope.GLOBAL
    )

    # Get the admin user
    admin = db.query(User).filter(
        User.id == admin_id,
        User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
    ).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )

    # Get permissions
    permissions = await admin_permission_service.get_user_permissions(
        db, admin, include_inherited=include_inherited
    )

    # Log the access
    await admin_permission_service._log_admin_activity(
        db, current_user, AdminActionType.SECURITY, "get_admin_permissions",
        f"Retrieved permissions for admin: {admin.email}",
        target_type="user", target_id=str(admin.id)
    )

    db.commit()

    return {
        "user_id": str(admin.id),
        "email": admin.email,
        "permissions": permissions,
        "total_count": len(permissions)
    }


@router.post("/admins/{admin_id}/permissions/grant", summary="Grant Permissions to Admin")
async def grant_permissions_to_admin(
    admin_id: str,
    request: PermissionGrantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Grant permissions to an admin user.

    **Required Permission:** users.manage.global
    **Security Level:** 4+
    **Risk Level:** HIGH
    """

    # Validate permission
    await admin_permission_service.validate_permission(
        db, current_user,
        ResourceType.USERS, PermissionAction.MANAGE, PermissionScope.GLOBAL
    )

    # Get the admin user
    admin = db.query(User).filter(
        User.id == admin_id,
        User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
    ).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )

    # Get permissions to grant
    permissions = db.query(AdminPermission).filter(
        AdminPermission.id.in_(request.permission_ids)
    ).all()

    if len(permissions) != len(request.permission_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more permissions not found"
        )

    # Grant each permission
    granted_permissions = []
    for permission in permissions:
        try:
            success = await admin_permission_service.grant_permission(
                db, current_user, admin, permission, request.expires_at
            )
            if success:
                granted_permissions.append(permission.name)
        except PermissionDeniedError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )

    # Log the operation
    await admin_permission_service._log_admin_activity(
        db, current_user, AdminActionType.SECURITY, "grant_permissions",
        f"Granted {len(granted_permissions)} permissions to {admin.email}. Reason: {request.reason}",
        target_type="user", target_id=str(admin.id),
        risk_level=RiskLevel.HIGH
    )

    db.commit()

    return {
        "message": f"Successfully granted {len(granted_permissions)} permissions",
        "granted_permissions": granted_permissions,
        "expires_at": request.expires_at.isoformat() if request.expires_at else None
    }


@router.post("/admins/{admin_id}/permissions/revoke", summary="Revoke Permissions from Admin")
async def revoke_permissions_from_admin(
    admin_id: str,
    request: PermissionRevokeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revoke permissions from an admin user.

    **Required Permission:** users.manage.global
    **Security Level:** 4+
    **Risk Level:** HIGH
    """

    # Validate permission
    await admin_permission_service.validate_permission(
        db, current_user,
        ResourceType.USERS, PermissionAction.MANAGE, PermissionScope.GLOBAL
    )

    # Get the admin user
    admin = db.query(User).filter(
        User.id == admin_id,
        User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
    ).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )

    # Get permissions to revoke
    permissions = db.query(AdminPermission).filter(
        AdminPermission.id.in_(request.permission_ids)
    ).all()

    if len(permissions) != len(request.permission_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more permissions not found"
        )

    # Revoke each permission
    revoked_permissions = []
    for permission in permissions:
        try:
            success = await admin_permission_service.revoke_permission(
                db, current_user, admin, permission
            )
            if success:
                revoked_permissions.append(permission.name)
        except PermissionDeniedError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )

    # Log the operation
    await admin_permission_service._log_admin_activity(
        db, current_user, AdminActionType.SECURITY, "revoke_permissions",
        f"Revoked {len(revoked_permissions)} permissions from {admin.email}. Reason: {request.reason}",
        target_type="user", target_id=str(admin.id),
        risk_level=RiskLevel.HIGH
    )

    db.commit()

    return {
        "message": f"Successfully revoked {len(revoked_permissions)} permissions",
        "revoked_permissions": revoked_permissions
    }


# === BULK OPERATIONS ===

@router.post("/admins/bulk-action", summary="Perform Bulk Actions on Admin Users")
async def bulk_admin_action(
    request: BulkUserActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform bulk actions on multiple admin users.

    **Required Permission:** users.manage.global
    **Security Level:** 4+
    **Risk Level:** HIGH
    """

    # Validate permission
    await admin_permission_service.validate_permission(
        db, current_user,
        ResourceType.USERS, PermissionAction.MANAGE, PermissionScope.GLOBAL
    )

    # Get admin users
    admins = db.query(User).filter(
        User.id.in_(request.user_ids),
        User.user_type.in_([UserType.ADMIN, UserType.SUPERUSER])
    ).all()

    if len(admins) != len(request.user_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more admin users not found"
        )

    # Perform bulk action
    processed_count = 0
    action_results = []

    for admin in admins:
        try:
            if request.action == "activate":
                admin.is_active = True
                admin.account_locked_until = None
            elif request.action == "deactivate":
                admin.is_active = False
            elif request.action == "lock":
                admin.account_locked_until = datetime.utcnow() + timedelta(hours=24)
            elif request.action == "unlock":
                admin.account_locked_until = None
                admin.failed_login_attempts = 0
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid action: {request.action}"
                )

            processed_count += 1
            action_results.append({
                "user_id": str(admin.id),
                "email": admin.email,
                "status": "success"
            })

        except Exception as e:
            action_results.append({
                "user_id": str(admin.id),
                "email": admin.email if admin else "unknown",
                "status": "error",
                "error": str(e)
            })

    # Log the bulk operation
    await admin_permission_service._log_admin_activity(
        db, current_user, AdminActionType.USER_MANAGEMENT, f"bulk_{request.action}",
        f"Bulk {request.action} on {processed_count} admin users. Reason: {request.reason}",
        risk_level=RiskLevel.HIGH
    )

    db.commit()

    return {
        "message": f"Bulk action completed. Processed {processed_count}/{len(request.user_ids)} users",
        "action": request.action,
        "results": action_results
    }