import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User
import json

# Configurar logger específico para auditoría admin
audit_logger = logging.getLogger('admin_audit')
audit_logger.setLevel(logging.INFO)

# Handler para archivo de logs de auditoría
handler = logging.FileHandler('/tmp/admin_audit.log')
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
audit_logger.addHandler(handler)

class AuditService:
    """Servicio para logs de auditoría administrativa"""
    
    @staticmethod
    def log_admin_login_attempt(
        email: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Registrar intento de login administrativo"""
        log_data = {
            'action': 'admin_login_attempt',
            'email': email,
            'success': success,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
            'user_agent': user_agent,
        }
        
        if not success and error_message:
            log_data['error'] = error_message
            
        audit_logger.warning(f"ADMIN_LOGIN_ATTEMPT: {json.dumps(log_data)}")
        
    @staticmethod
    def log_admin_login_success(
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        portal_type: str = 'admin-secure-portal'
    ):
        """Registrar login administrativo exitoso"""
        log_data = {
            'action': 'admin_login_success',
            'user_id': str(user.id),
            'email': user.email,
            'user_type': user.user_type.value,
            'portal_type': portal_type,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
            'user_agent': user_agent,
        }
        
        audit_logger.info(f"ADMIN_LOGIN_SUCCESS: {json.dumps(log_data)}")
        
    @staticmethod
    def log_admin_access_denied(
        email: str,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Registrar acceso denegado a portal admin"""
        log_data = {
            'action': 'admin_access_denied',
            'email': email,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
            'user_agent': user_agent,
        }
        
        audit_logger.warning(f"ADMIN_ACCESS_DENIED: {json.dumps(log_data)}")
        
    @staticmethod
    def log_admin_action(
        user: User,
        action: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """Registrar acción administrativa específica"""
        log_data = {
            'action': 'admin_action',
            'user_id': str(user.id),
            'email': user.email,
            'admin_action': action,
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
        }
        
        audit_logger.info(f"ADMIN_ACTION: {json.dumps(log_data)}")