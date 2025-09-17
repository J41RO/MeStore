# ~/app/models/admin_activity_log.py
# ---------------------------------------------------------------------------------------------
# MeStore - Admin Activity Log Model
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: admin_activity_log.py
# Ruta: ~/app/models/admin_activity_log.py
# Autor: Jairo - Backend Senior Developer
# Fecha de Creación: 2025-09-14
# Última Actualización: 2025-09-14
# Versión: 1.0.0
# Propósito: SUPERUSER Admin Panel - Comprehensive Activity Logging System
#
# TASK_002A: SUPERUSER Admin Panel Backend - Enterprise Security Layer
# - Comprehensive audit logging for all admin actions
# - Security event monitoring and alerting
# - Compliance reporting capabilities
# - Performance analytics for admin operations
#
# ---------------------------------------------------------------------------------------------

"""
SUPERUSER Admin Activity Logging System.

Este módulo implementa el sistema de logging comprehensivo para administradores:
- Complete audit trail for all admin actions
- Security event detection and monitoring
- Performance analytics and reporting
- Compliance audit capabilities
- Real-time alerting for suspicious activities
- Geographic and device tracking
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON, ForeignKey, Float
from sqlalchemy import Index
from app.core.types import UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum
import uuid

from app.models.base import BaseModel


class AdminActionType(str, PyEnum):
    """
    Enterprise Admin Action Types for comprehensive logging.

    Categories of admin actions to track:
        AUTHENTICATION: Login, logout, password changes
        USER_MANAGEMENT: User CRUD operations, role changes
        VENDOR_MANAGEMENT: Vendor approvals, rejections, modifications
        FINANCIAL: Transaction reviews, commission adjustments
        SYSTEM_CONFIG: Configuration changes, settings updates
        DATA_EXPORT: Data exports and reporting
        SECURITY: Permission changes, security events
        AUDIT: Audit log access and reviews
        MONITORING: System monitoring activities
        EMERGENCY: Emergency actions and overrides
    """
    AUTHENTICATION = "AUTHENTICATION"
    USER_MANAGEMENT = "USER_MANAGEMENT"
    VENDOR_MANAGEMENT = "VENDOR_MANAGEMENT"
    FINANCIAL = "FINANCIAL"
    SYSTEM_CONFIG = "SYSTEM_CONFIG"
    DATA_EXPORT = "DATA_EXPORT"
    SECURITY = "SECURITY"
    AUDIT = "AUDIT"
    MONITORING = "MONITORING"
    EMERGENCY = "EMERGENCY"


class ActionResult(str, PyEnum):
    """
    Enterprise Action Results for audit tracking.

    Possible outcomes of admin actions:
        SUCCESS: Action completed successfully
        FAILURE: Action failed due to error
        PARTIAL: Action partially completed
        BLOCKED: Action blocked by security policies
        PENDING: Action requires additional approval
        CANCELLED: Action was cancelled by user
        TIMEOUT: Action timed out during execution
    """
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"


class RiskLevel(str, PyEnum):
    """
    Risk levels for admin actions.

    Classification of action risk levels:
        LOW: Routine operations with minimal impact
        MEDIUM: Standard operations with moderate impact
        HIGH: Sensitive operations with significant impact
        CRITICAL: High-risk operations requiring special attention
        EMERGENCY: Emergency operations bypassing normal controls
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AdminActivityLog(BaseModel):
    """
    Enterprise Admin Activity Log Model.

    Comprehensive logging system for SUPERUSER admin operations:
    - Complete audit trail for all administrative actions
    - Security event detection and monitoring
    - Performance metrics and analytics
    - Compliance reporting capabilities
    - Geographic and device tracking
    - Real-time alerting for suspicious activities
    - Data retention and archival support
    """

    __tablename__ = "admin_activity_logs"

    # === PRIMARY KEY ===
    id = Column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Unique activity log identifier"
    )

    # === ADMIN USER INFORMATION ===
    admin_user_id = Column(
        UUID(),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="Admin user who performed the action"
    )

    admin_email = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Email of admin user (for audit even if user deleted)"
    )

    admin_full_name = Column(
        String(200),
        nullable=True,
        comment="Full name of admin user at time of action"
    )

    # === ACTION DETAILS ===
    action_type = Column(
        SQLEnum(AdminActionType),
        nullable=False,
        index=True,
        comment="Type of admin action performed"
    )

    action_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Specific action name (e.g., 'create_user', 'approve_vendor')"
    )

    action_description = Column(
        Text,
        nullable=True,
        comment="Detailed description of the action performed"
    )

    # === TARGET INFORMATION ===
    target_type = Column(
        String(50),
        nullable=True,
        comment="Type of target object (user, vendor, order, etc.)"
    )

    target_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="ID of the target object"
    )

    target_identifier = Column(
        String(200),
        nullable=True,
        comment="Human-readable identifier of target (email, name, etc.)"
    )

    # === ACTION RESULT AND METADATA ===
    result = Column(
        SQLEnum(ActionResult),
        nullable=False,
        default=ActionResult.SUCCESS,
        index=True,
        comment="Result of the action"
    )

    risk_level = Column(
        SQLEnum(RiskLevel),
        nullable=False,
        default=RiskLevel.LOW,
        index=True,
        comment="Risk level of the action"
    )

    # === TECHNICAL DETAILS ===
    endpoint = Column(
        String(200),
        nullable=True,
        comment="API endpoint that was called"
    )

    http_method = Column(
        String(10),
        nullable=True,
        comment="HTTP method used (GET, POST, PUT, DELETE, etc.)"
    )

    request_data = Column(
        JSON,
        nullable=True,
        comment="Request data/payload (sensitive data filtered)"
    )

    response_data = Column(
        JSON,
        nullable=True,
        comment="Response data (sensitive data filtered)"
    )

    # === SECURITY AND CONTEXT ===
    ip_address = Column(
        String(45),  # IPv4 or IPv6 address
        nullable=True,
        index=True,
        comment="IP address of the admin user"
    )

    user_agent = Column(
        Text,
        nullable=True,
        comment="User agent string of the client"
    )

    session_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Session ID for correlation"
    )

    device_fingerprint = Column(
        String(255),
        nullable=True,
        comment="Device fingerprint for security tracking"
    )

    # === GEOGRAPHIC INFORMATION ===
    country_code = Column(
        String(2),
        nullable=True,
        comment="Country code derived from IP address"
    )

    region = Column(
        String(100),
        nullable=True,
        comment="Geographic region"
    )

    city = Column(
        String(100),
        nullable=True,
        comment="Geographic city"
    )

    timezone = Column(
        String(50),
        nullable=True,
        comment="User timezone"
    )

    # === PERFORMANCE METRICS ===
    execution_time_ms = Column(
        Float,
        nullable=True,
        comment="Action execution time in milliseconds"
    )

    cpu_usage_percent = Column(
        Float,
        nullable=True,
        comment="CPU usage during action execution"
    )

    memory_usage_mb = Column(
        Float,
        nullable=True,
        comment="Memory usage during action execution"
    )

    # === ERROR INFORMATION ===
    error_code = Column(
        String(50),
        nullable=True,
        comment="Error code if action failed"
    )

    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if action failed"
    )

    error_stack_trace = Column(
        Text,
        nullable=True,
        comment="Stack trace for debugging (filtered for security)"
    )

    # === AUDIT AND COMPLIANCE ===
    requires_review = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this action requires manual review"
    )

    is_suspicious = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether this action was flagged as suspicious"
    )

    compliance_tags = Column(
        JSON,
        nullable=True,
        comment="Compliance-related tags and metadata"
    )

    retention_policy = Column(
        String(50),
        default="STANDARD",
        nullable=False,
        comment="Data retention policy (STANDARD, LONG_TERM, PERMANENT)"
    )

    # === ADDITIONAL METADATA ===
    tags = Column(
        JSON,
        nullable=True,
        comment="Additional tags for categorization and filtering"
    )

    custom_fields = Column(
        JSON,
        nullable=True,
        comment="Custom fields for specific admin actions"
    )

    correlation_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Correlation ID for tracking related actions"
    )

    # === NOTIFICATIONS ===
    alert_sent = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether security alert was sent for this action"
    )

    alert_level = Column(
        String(20),
        nullable=True,
        comment="Level of alert sent (INFO, WARNING, CRITICAL)"
    )

    # === RELATIONSHIPS ===
    admin_user = relationship(
        "User",
        foreign_keys=[admin_user_id],
        back_populates="admin_activity_logs"
    )

    # === INDEXES FOR PERFORMANCE ===
    __table_args__ = (
        Index('ix_admin_activity_logs_user_time', 'admin_user_id', 'created_at'),
        Index('ix_admin_activity_logs_action_result', 'action_type', 'result'),
        Index('ix_admin_activity_logs_risk_time', 'risk_level', 'created_at'),
        Index('ix_admin_activity_logs_suspicious', 'is_suspicious', 'created_at'),
        Index('ix_admin_activity_logs_ip_time', 'ip_address', 'created_at'),
        Index('ix_admin_activity_logs_target', 'target_type', 'target_id'),
        Index('ix_admin_activity_logs_correlation', 'correlation_id'),
        Index('ix_admin_activity_logs_session', 'session_id', 'created_at'),
        Index('ix_admin_activity_logs_compliance', 'requires_review', 'risk_level'),
    )

    # === VALIDATION METHODS ===

    @validates('risk_level')
    def validate_risk_level(self, key, value):
        """Validate risk level and set appropriate flags."""
        if value in [RiskLevel.CRITICAL, RiskLevel.EMERGENCY]:
            self.requires_review = True

        return value

    @validates('execution_time_ms')
    def validate_execution_time(self, key, value):
        """Validate execution time is reasonable."""
        if value and value < 0:
            raise ValueError("Execution time cannot be negative")
        if value and value > 300000:  # 5 minutes
            # Flag as suspicious if execution takes too long
            self.is_suspicious = True
        return value

    # === BUSINESS LOGIC METHODS ===

    def mark_as_suspicious(self, reason: str = None) -> None:
        """Mark this activity log entry as suspicious."""
        self.is_suspicious = True
        self.requires_review = True

        if reason:
            if not self.tags:
                self.tags = {}
            self.tags['suspicious_reason'] = reason

    def add_compliance_tag(self, tag: str, value: Any) -> None:
        """Add a compliance-related tag."""
        if not self.compliance_tags:
            self.compliance_tags = {}
        self.compliance_tags[tag] = value

    def set_performance_metrics(self, execution_time: float, cpu_usage: float = None, memory_usage: float = None) -> None:
        """Set performance metrics for the action."""
        self.execution_time_ms = execution_time
        if cpu_usage:
            self.cpu_usage_percent = cpu_usage
        if memory_usage:
            self.memory_usage_mb = memory_usage

    def should_trigger_alert(self) -> bool:
        """Determine if this activity should trigger a security alert."""
        return (
            self.is_suspicious or
            self.risk_level in [RiskLevel.CRITICAL, RiskLevel.EMERGENCY] or
            self.result in [ActionResult.BLOCKED, ActionResult.FAILURE] or
            self.requires_review
        )

    def get_alert_level(self) -> str:
        """Get appropriate alert level for this activity."""
        if self.risk_level == RiskLevel.EMERGENCY or self.is_suspicious:
            return "CRITICAL"
        elif self.risk_level == RiskLevel.CRITICAL or self.result == ActionResult.BLOCKED:
            return "WARNING"
        else:
            return "INFO"

    # === SERIALIZATION METHODS ===

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert activity log to dictionary for API responses."""
        data = {
            'id': str(self.id),
            'admin_user_id': str(self.admin_user_id) if self.admin_user_id else None,
            'admin_email': self.admin_email,
            'admin_full_name': self.admin_full_name,
            'action_type': self.action_type.value,
            'action_name': self.action_name,
            'action_description': self.action_description,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'target_identifier': self.target_identifier,
            'result': self.result.value,
            'risk_level': self.risk_level.value,
            'endpoint': self.endpoint,
            'http_method': self.http_method,
            'ip_address': str(self.ip_address) if self.ip_address else None,
            'country_code': self.country_code,
            'region': self.region,
            'city': self.city,
            'timezone': self.timezone,
            'execution_time_ms': self.execution_time_ms,
            'requires_review': self.requires_review,
            'is_suspicious': self.is_suspicious,
            'alert_sent': self.alert_sent,
            'alert_level': self.alert_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_sensitive:
            # Include sensitive data only for authorized users
            data.update({
                'request_data': self.request_data,
                'response_data': self.response_data,
                'user_agent': self.user_agent,
                'session_id': self.session_id,
                'device_fingerprint': self.device_fingerprint,
                'error_message': self.error_message,
                'error_code': self.error_code,
                'tags': self.tags,
                'compliance_tags': self.compliance_tags,
                'custom_fields': self.custom_fields
            })

        return data

    def to_audit_dict(self) -> Dict[str, Any]:
        """Convert to dictionary specifically for audit purposes."""
        return {
            'log_id': str(self.id),
            'timestamp': self.created_at.isoformat() if self.created_at else None,
            'admin_identifier': self.admin_email or str(self.admin_user_id),
            'action': f"{self.action_type.value}.{self.action_name}",
            'target': f"{self.target_type}:{self.target_identifier}" if self.target_type else None,
            'result': self.result.value,
            'risk_level': self.risk_level.value,
            'ip_address': str(self.ip_address) if self.ip_address else None,
            'location': f"{self.city}, {self.region}, {self.country_code}" if self.city else None,
            'execution_time': self.execution_time_ms,
            'requires_review': self.requires_review,
            'is_suspicious': self.is_suspicious,
            'compliance_tags': self.compliance_tags
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<AdminActivityLog(id={self.id}, action='{self.action_name}', admin='{self.admin_email}')>"

    def __str__(self) -> str:
        """Human-readable string representation."""
        timestamp = self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "N/A"
        return f"[{timestamp}] {self.admin_email} performed {self.action_name} - {self.result.value}"


# Utility functions for creating common activity log entries

def create_authentication_log(admin_user, action_name: str, result: ActionResult,
                            ip_address: str = None, user_agent: str = None) -> AdminActivityLog:
    """Create authentication-related activity log entry."""
    return AdminActivityLog(
        admin_user_id=admin_user.id,
        admin_email=admin_user.email,
        admin_full_name=admin_user.full_name,
        action_type=AdminActionType.AUTHENTICATION,
        action_name=action_name,
        result=result,
        risk_level=RiskLevel.MEDIUM if result == ActionResult.SUCCESS else RiskLevel.HIGH,
        ip_address=ip_address,
        user_agent=user_agent
    )

def create_user_management_log(admin_user, action_name: str, target_user,
                             result: ActionResult, request_data: dict = None) -> AdminActivityLog:
    """Create user management activity log entry."""
    return AdminActivityLog(
        admin_user_id=admin_user.id,
        admin_email=admin_user.email,
        admin_full_name=admin_user.full_name,
        action_type=AdminActionType.USER_MANAGEMENT,
        action_name=action_name,
        target_type="user",
        target_id=str(target_user.id) if target_user else None,
        target_identifier=target_user.email if target_user else None,
        result=result,
        risk_level=RiskLevel.HIGH if action_name in ['delete_user', 'change_user_role'] else RiskLevel.MEDIUM,
        request_data=request_data
    )