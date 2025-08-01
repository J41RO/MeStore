# ~/app/services/otp_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio OTP
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Servicio OTP para MeStore.

Este módulo maneja la generación, validación y gestión de códigos OTP:
- Generación de códigos seguros de 6 dígitos
- Validación de códigos con expiración
- Control de intentos fallidos
- Gestión de cooldowns entre envíos
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.user import User


class OTPService:
    """Servicio para gestión completa de códigos OTP."""
    
    def __init__(self):
        """Inicializar servicio OTP con configuración."""
        self.code_length = 6
        self.expiry_minutes = 10  # OTP válido por 10 minutos
        self.max_attempts = 5     # Máximo 5 intentos fallidos
        self.cooldown_seconds = 60  # 1 minuto entre envíos
        
    def generate_otp_code(self) -> str:
        """
        Genera un código OTP de 6 dígitos.
        
        Returns:
            str: Código OTP de 6 dígitos numéricos
        """
        return ''.join(random.choices(string.digits, k=self.code_length))
    
    def create_otp_for_user(
        self, 
        db: Session, 
        user: User, 
        otp_type: str
    ) -> Tuple[str, datetime]:
        """
        Crea y asigna un código OTP a un usuario.
        
        Args:
            db: Sesión de base de datos
            user: Usuario al que asignar el OTP
            otp_type: Tipo de OTP ('EMAIL' o 'SMS')
            
        Returns:
            Tuple[str, datetime]: Código OTP y fecha de expiración
        """
        # Generar código y calcular expiración
        otp_code = self.generate_otp_code()
        expires_at = datetime.utcnow() + timedelta(minutes=self.expiry_minutes)
        
        # Asignar al usuario
        user.otp_secret = otp_code
        user.otp_expires_at = expires_at
        user.otp_type = otp_type
        user.last_otp_sent = datetime.utcnow()
        user.otp_attempts = 0  # Reiniciar intentos al generar nuevo código
        
        # Guardar en base de datos
        db.commit()
        db.refresh(user)
        
        return otp_code, expires_at
    
    def validate_otp_code(
        self, 
        db: Session, 
        user: User, 
        provided_code: str
    ) -> Tuple[bool, str]:
        """
        Valida un código OTP proporcionado por el usuario.
        
        Args:
            db: Sesión de base de datos
            user: Usuario que intenta validar
            provided_code: Código proporcionado por el usuario
            
        Returns:
            Tuple[bool, str]: (Es válido, Mensaje de resultado)
        """
        # Verificar si hay código activo
        if not user.otp_secret:
            return False, "No hay código OTP activo"
        
        # Verificar si está bloqueado por intentos
        if user.is_otp_blocked():
            return False, "Demasiados intentos fallidos. Solicite un nuevo código"
        
        # Verificar expiración
        if not user.is_otp_valid():
            return False, "Código OTP expirado"
        
        # Validar código
        if user.otp_secret == provided_code:
            # Código correcto - limpiar OTP y marcar como verificado
            self._clear_otp_data(db, user)
            
            # Marcar email o teléfono como verificado según tipo
            if user.otp_type == "EMAIL":
                user.email_verified = True
            elif user.otp_type == "SMS":
                user.phone_verified = True
            
            db.commit()
            db.refresh(user)
            
            return True, "Código OTP válido. Verificación completada"
        else:
            # Código incorrecto - incrementar intentos
            user.increment_otp_attempts()
            db.commit()
            db.refresh(user)
            
            remaining_attempts = self.max_attempts - user.otp_attempts
            if remaining_attempts <= 0:
                return False, "Código incorrecto. Máximo de intentos alcanzado"
            else:
                return False, f"Código incorrecto. Le quedan {remaining_attempts} intentos"
    
    def can_send_otp(self, user: User) -> Tuple[bool, str]:
        """
        Verifica si se puede enviar un nuevo OTP al usuario.
        
        Args:
            user: Usuario que solicita OTP
            
        Returns:
            Tuple[bool, str]: (Puede enviar, Mensaje explicativo)
        """
        # Verificar cooldown
        if not user.can_request_otp():
            return False, f"Debe esperar {self.cooldown_seconds} segundos entre envíos"
        
        # Verificar si está bloqueado
        if user.is_otp_blocked():
            return False, "Demasiados intentos fallidos. Contacte soporte"
        
        return True, "Puede solicitar nuevo código OTP"
    
    def _clear_otp_data(self, db: Session, user: User):
        """
        Limpia todos los datos OTP del usuario.
        
        Args:
            db: Sesión de base de datos
            user: Usuario a limpiar
        """
        user.otp_secret = None
        user.otp_expires_at = None
        user.otp_type = None
        user.otp_attempts = 0
        # Mantener last_otp_sent para cooldown
    
    def cleanup_expired_otps(self, db: Session):
        """
        Limpia códigos OTP expirados de la base de datos.
        
        Args:
            db: Sesión de base de datos
        """
        expired_users = db.query(User).filter(
            User.otp_expires_at < datetime.utcnow(),
            User.otp_secret.isnot(None)
        ).all()
        
        for user in expired_users:
            self._clear_otp_data(db, user)
        
        if expired_users:
            db.commit()
            
        return len(expired_users)
