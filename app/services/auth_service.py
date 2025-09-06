"""
~/app/services/auth_service.py
-------------------------------------------------------------------------------------
MESTOCKER - Servicio de Autenticación
Copyright (c) 2025 Jairo. Todos los derechos reservados.
Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
-------------------------------------------------------------------------------------

Nombre del Archivo: auth_service.py
Ruta: ~/app/services/auth_service.py  
Autor: Jairo
Fecha de Creación: 2025-07-31
Última Actualización: 2025-07-31
Versión: 1.0.0
Propósito: Servicio centralizado de autenticación con manejo async/sync correcto
           para prevenir RuntimeError: Event loop is closed

Modificaciones:
2025-07-31 - Creación con corrección async/sync para bcrypt

-------------------------------------------------------------------------------------
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.otp_service import OTPService
from app.services.email_service import EmailService
from app.services.sms_service import SMSService

# Configurar logger
logger = logging.getLogger(__name__)
from typing import Tuple


class AuthService:
    """
    Servicio de autenticación con manejo correcto async/sync.
    
    Resuelve el problema de RuntimeError: Event loop is closed
    usando ThreadPoolExecutor para operaciones bcrypt.
    """
    
    def __init__(self):
        # Servicios OTP integrados
        self.otp_service = OTPService()
        self.email_service = EmailService()
        self.sms_service = SMSService()
        # Servicios OTP integrados
        self.otp_service = OTPService()
        self.email_service = EmailService()
        self.sms_service = SMSService()
        """Inicializar servicio con contexto bcrypt y thread pool."""
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto"
        )
        # ThreadPoolExecutor para operaciones bcrypt async
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="bcrypt")
    
    async def get_password_hash(self, password: str) -> str:
        """
        Hash password usando bcrypt con ThreadPoolExecutor.
        
        Esta función corrige el error RuntimeError: Event loop is closed
        ejecutando bcrypt en thread separado.
        
        Args:
            password: Password en texto plano
            
        Returns:
            Password hasheado con bcrypt
        """
        loop = asyncio.get_event_loop()
        
        # Ejecutar bcrypt.hash en thread separado para evitar bloqueo del event loop
        hashed_password = await loop.run_in_executor(
            self.executor,
            self._hash_password_sync,
            password
        )
        
        return hashed_password
    
    def _hash_password_sync(self, password: str) -> str:
        """
        Función sync interna para hash con bcrypt.
        
        Args:
            password: Password a hashear
            
        Returns:
            Password hasheado
        """
        return self.pwd_context.hash(password)
    
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verificar password usando bcrypt con ThreadPoolExecutor.
        
        Args:
            plain_password: Password en texto plano
            hashed_password: Password hasheado a verificar
            
        Returns:
            True si coincide, False si no
        """
        loop = asyncio.get_event_loop()
        
        # Ejecutar bcrypt.verify en thread separado
        is_valid = await loop.run_in_executor(
            self.executor,
            self._verify_password_sync,
            plain_password,
            hashed_password
        )
        
        return is_valid
    
    def _verify_password_sync(self, plain_password: str, hashed_password: str) -> bool:
        """
        Función sync interna para verificar password.
        
        Args:
            plain_password: Password en texto plano
            hashed_password: Password hasheado
            
        Returns:
            True si coincide, False si no
        """
        return self.pwd_context.verify(plain_password, hashed_password)


    async def create_user(
        self,
        db,
        email: str,
        password: str,
        user_type = None,
        is_active: bool = True,
        **additional_fields
    ):
        """
        Crear un nuevo usuario en la base de datos
        
        Args:
            db: Sesión de base de datos async
            email: Email del usuario
            password: Contraseña en texto plano
            user_type: Tipo de usuario
            is_active: Si el usuario está activo
            **additional_fields: Campos adicionales del usuario
            
        Returns:
            User: Objeto usuario creado
        """
        from app.models.user import User, UserType
        from sqlalchemy import select
        
        # Establecer tipo por defecto
        if user_type is None:
            user_type = UserType.COMPRADOR
        
        # Verificar si el usuario ya existe
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValueError(f"Usuario con email {email} ya existe")
        
        # Hash de la contraseña
        password_hash = await self.get_password_hash(password)
        
        # Crear nuevo usuario
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'user_type': user_type,
            'is_active': is_active,
            **additional_fields
        }
        
        new_user = User(**user_data)
        
        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user
        except Exception as e:
            await db.rollback()
            raise ValueError(f"Error al crear usuario: {str(e)}")
    

    # === MÉTODOS OTP PARA VERIFICACIÓN EMAIL/SMS ===

    async def send_email_verification_otp(
        self, 
        db: Session, 
        user: User
    ) -> Tuple[bool, str]:
        """
        Envía código OTP por email para verificación.

        Args:
            db: Sesión de base de datos
            user: Usuario que solicita verificación

        Returns:
            Tuple[bool, str]: (Éxito, Mensaje)
        """
        try:
            # Verificar si puede enviar OTP
            can_send, message = self.otp_service.can_send_otp(user)
            if not can_send:
                return False, message

            # Generar código OTP
            otp_code, expires_at = self.otp_service.create_otp_for_user(
                db=db, 
                user=user, 
                otp_type="EMAIL"
            )

            # Enviar email
            email_sent = self.email_service.send_otp_email(
                email=user.email,
                otp_code=otp_code,
                user_name=user.nombre
            )

            if email_sent:
                return True, f"Código enviado a {user.email}. Válido por 10 minutos"
            else:
                return False, "Error enviando email. Intente nuevamente"

        except Exception as e:
            return False, f"Error interno: {str(e)}"

    async def send_sms_verification_otp(
        self, 
        db: Session, 
        user: User
    ) -> Tuple[bool, str]:
        """
        Envía código OTP por SMS para verificación.

        Args:
            db: Sesión de base de datos
            user: Usuario que solicita verificación

        Returns:
            Tuple[bool, str]: (Éxito, Mensaje)
        """
        try:
            # Verificar que tiene teléfono
            if not user.telefono:
                return False, "Usuario no tiene teléfono registrado"

            # Verificar si puede enviar OTP
            can_send, message = self.otp_service.can_send_otp(user)
            if not can_send:
                return False, message

            # Generar código OTP
            otp_code, expires_at = self.otp_service.create_otp_for_user(
                db=db, 
                user=user, 
                otp_type="SMS"
            )

            # Enviar SMS
            sms_sent = self.sms_service.send_otp_sms(
                phone_number=user.telefono,
                otp_code=otp_code,
                user_name=user.nombre
            )

            if sms_sent:
                return True, f"Código enviado a {user.telefono}. Válido por 10 minutos"
            else:
                return False, "Error enviando SMS. Intente nuevamente"

        except Exception as e:
            return False, f"Error interno: {str(e)}"

    async def verify_otp_code(
        self, 
        db: Session, 
        user: User, 
        otp_code: str
    ) -> Tuple[bool, str]:
        """
        Verifica un código OTP proporcionado por el usuario.

        Args:
            db: Sesión de base de datos
            user: Usuario que intenta verificar
            otp_code: Código proporcionado

        Returns:
            Tuple[bool, str]: (Es válido, Mensaje)
        """
        try:
            return self.otp_service.validate_otp_code(db, user, otp_code)
        except Exception as e:
            return False, f"Error verificando código: {str(e)}"

    async def get_user_verification_status(self, user: User) -> dict:
        """
        Obtiene el estado de verificación completo del usuario.

        Args:
            user: Usuario a consultar

        Returns:
            dict: Estado de verificaciones
        """
        return {
            'email_verified': user.email_verified,
            'phone_verified': user.phone_verified,
            'has_active_otp': user.otp_secret is not None,
            'otp_type': user.otp_type,
            'otp_expires_at': user.otp_expires_at.isoformat() if user.otp_expires_at else None,
            'can_request_new_otp': user.can_request_otp(),
            'is_otp_blocked': user.is_otp_blocked(),
            'otp_attempts': user.otp_attempts
        }

    async def cleanup_expired_otps(self, db: Session) -> int:
        """
        Limpia códigos OTP expirados (método de mantenimiento).

        Args:
            db: Sesión de base de datos

        Returns:
            int: Número de códigos limpiados
        """
        try:
            return self.otp_service.cleanup_expired_otps(db)
        except Exception as e:
            return 0


    # === MÉTODOS PARA RECUPERACIÓN DE CONTRASEÑA ===

    async def send_password_reset_email(
        self, 
        db: Session, 
        email: str
    ) -> Tuple[bool, str]:
        """
        Envía email de recuperación de contraseña.

        Args:
            db: Sesión de base de datos
            email: Email del usuario

        Returns:
            Tuple[bool, str]: (Éxito, Mensaje)
        """
        from app.models.user import User
        from app.services.email_service import EmailService
        import secrets
        from datetime import datetime, timedelta

        try:
            # Buscar usuario por email
            user = db.query(User).filter(User.email == email).first()
            if not user:
                # Por seguridad, no revelar si el email existe
                return True, "Si el email existe, recibirás instrucciones de recuperación"

            # Verificar cooldown (5 minutos entre requests)
            if not user.can_request_password_reset():
                return False, "Debe esperar 5 minutos antes de solicitar otro reset"

            # Verificar si está bloqueado por intentos
            if user.is_reset_blocked():
                return False, "Demasiados intentos de reset. Contacte soporte"

            # Generar token seguro
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=1)  # Expira en 1 hora

            # Asignar token al usuario
            user.reset_token = reset_token
            user.reset_token_expires_at = expires_at
            user.last_reset_request = datetime.utcnow()

            # Guardar en base de datos
            db.commit()
            db.refresh(user)

            # Enviar email
            email_service = EmailService()
            email_sent = email_service.send_password_reset_email(
                email=user.email,
                reset_token=reset_token,
                user_name=user.nombre
            )

            if email_sent:
                return True, "Se ha enviado un enlace de recuperación a tu email"
            else:
                # Limpiar token si no se pudo enviar
                user.reset_token = None
                user.reset_token_expires_at = None
                db.commit()
                return False, "Error enviando email de recuperación"

        except Exception as e:
            logger.error(f"Error en send_password_reset_email: {str(e)}")
            return False, "Error interno del servidor"

    async def reset_password_with_token(
        self, 
        db: Session, 
        token: str, 
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Resetea contraseña usando token de recuperación.

        Args:
            db: Sesión de base de datos
            token: Token de reset
            new_password: Nueva contraseña

        Returns:
            Tuple[bool, str]: (Éxito, Mensaje)
        """
        from app.models.user import User

        try:
            # Buscar usuario por token
            user = db.query(User).filter(User.reset_token == token).first()
            if not user:
                return False, "Token de recuperación inválido"

            # Verificar que el token no haya expirado
            if not user.is_reset_token_valid():
                # Limpiar token expirado
                user.clear_reset_data()
                db.commit()
                return False, "El enlace de recuperación ha expirado"

            # Verificar si está bloqueado por intentos
            if user.is_reset_blocked():
                return False, "Demasiados intentos fallidos. Contacte soporte"

            # Hash de la nueva contraseña
            password_hash = await self.get_password_hash(new_password)

            # Actualizar contraseña y limpiar datos de reset
            user.password_hash = password_hash
            user.clear_reset_data()

            # Guardar cambios
            db.commit()
            db.refresh(user)

            logger.info(f"Contraseña reseteada exitosamente para usuario {user.email}")
            return True, "Contraseña actualizada exitosamente"

        except Exception as e:
            logger.error(f"Error en reset_password_with_token: {str(e)}")
            return False, "Error interno del servidor"

    async def cleanup_expired_reset_tokens(self, db: Session) -> int:
        """
        Limpia tokens de reset expirados de la base de datos.

        Args:
            db: Sesión de base de datos

        Returns:
            int: Número de tokens limpiados
        """
        from app.models.user import User
        from datetime import datetime

        try:
            expired_users = db.query(User).filter(
                User.reset_token_expires_at < datetime.utcnow(),
                User.reset_token.isnot(None)
            ).all()

            for user in expired_users:
                user.clear_reset_data()

            if expired_users:
                db.commit()

            logger.info(f"Limpiados {len(expired_users)} tokens de reset expirados")
            return len(expired_users)

        except Exception as e:
            logger.error(f"Error en cleanup_expired_reset_tokens: {str(e)}")
            return 0
    def __del__(self):
        """Cleanup del ThreadPoolExecutor al destruir el objeto."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)