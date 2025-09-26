# ~/app/services/smtp_email_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio Email SMTP
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Servicio Email SMTP para MeStore.

Este módulo maneja el envío de emails usando SMTP (Gmail, Outlook, etc):
- Emails de verificación con códigos OTP
- Emails de recuperación de contraseña
- Templates HTML para emails atractivos
- Configuración SMTP flexible
- Manejo de errores de envío
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional
from email.header import Header

logger = logging.getLogger(__name__)


class SMTPEmailConfig:
    """Configuración SMTP para emails"""

    def __init__(self):
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
        self.FRONTEND_URL = self._get_frontend_url()

        # Configuración SMTP
        self.EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
        self.EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
        self.EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
        self.EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
        self.FROM_EMAIL = os.getenv('FROM_EMAIL', self.EMAIL_HOST_USER)
        self.FROM_NAME = os.getenv('FROM_NAME', 'MeStore')

    def _get_frontend_url(self) -> str:
        if self.ENVIRONMENT == 'production':
            return os.getenv('FRONTEND_URL', 'https://tudominio.com')
        return os.getenv('DEV_FRONTEND_URL', 'http://192.168.1.137:5173')


class SMTPEmailService:
    """Servicio para envío de emails usando SMTP."""

    def __init__(self):
        """Inicializar servicio de email SMTP."""
        self.config = SMTPEmailConfig()

        if not self.config.EMAIL_HOST_USER or not self.config.EMAIL_HOST_PASSWORD:
            logger.warning("EMAIL_HOST_USER o EMAIL_HOST_PASSWORD no configurados. Email service en modo simulación")
            self.simulation_mode = True
        else:
            self.simulation_mode = False

    def _send_smtp_email(self, to_email: str, subject: str, html_content: str, plain_content: str) -> bool:
        """
        Envía email usando SMTP.

        Args:
            to_email: Email destino
            subject: Asunto del email
            html_content: Contenido HTML
            plain_content: Contenido texto plano

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # Crear mensaje multipart
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config.FROM_NAME} <{self.config.FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = Header(subject, 'utf-8')

            # Agregar contenido texto plano y HTML
            part_text = MIMEText(plain_content, 'plain', 'utf-8')
            part_html = MIMEText(html_content, 'html', 'utf-8')

            msg.attach(part_text)
            msg.attach(part_html)

            # Conectar y enviar
            server = smtplib.SMTP(self.config.EMAIL_HOST, self.config.EMAIL_PORT)

            if self.config.EMAIL_USE_TLS:
                server.starttls()

            server.login(self.config.EMAIL_HOST_USER, self.config.EMAIL_HOST_PASSWORD)
            server.send_message(msg)
            server.quit()

            logger.info(f"Email SMTP enviado exitosamente a {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email SMTP: {str(e)}")
            return False

    def send_otp_email(
        self,
        email: str,
        otp_code: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Envía email con código OTP de verificación.

        Args:
            email: Email destino
            otp_code: Código OTP de 6 dígitos
            user_name: Nombre del usuario (opcional)

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            if self.simulation_mode:
                logger.info(f"SIMULACIÓN EMAIL SMTP - Para: {email}, OTP: {otp_code}")
                print(f"📧 SIMULACIÓN EMAIL OTP:")
                print(f"   Para: {email}")
                print(f"   Código: {otp_code}")
                print(f"   Usuario: {user_name}")
                return True

            # Preparar contenido del email
            subject = f"MeStore - Código de verificación: {otp_code}"

            # Contenido HTML
            html_content = self._create_otp_html_template(
                otp_code=otp_code,
                user_name=user_name or "Usuario"
            )

            # Contenido texto plano
            plain_content = self._create_otp_plain_template(
                otp_code=otp_code,
                user_name=user_name or "Usuario"
            )

            return self._send_smtp_email(email, subject, html_content, plain_content)

        except Exception as e:
            logger.error(f"Excepción enviando email OTP: {str(e)}")
            return False

    def send_password_reset_email(
        self,
        email: str,
        reset_token: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Envía email con enlace para reset de contraseña.

        Args:
            email: Email destino
            reset_token: Token de reset único
            user_name: Nombre del usuario (opcional)

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            if self.simulation_mode:
                reset_url = f"{self.config.FRONTEND_URL}/reset-password?token={reset_token}"
                logger.info(f"SIMULACIÓN EMAIL RESET - Para: {email}, URL: {reset_url}")
                print(f"🔐 SIMULACIÓN EMAIL RESET PASSWORD:")
                print(f"   Para: {email}")
                print(f"   Token: {reset_token}")
                print(f"   URL: {reset_url}")
                return True

            subject = "Recuperación de Contraseña - MeStore"
            name = user_name or "Usuario"

            html_content = self._create_reset_html_template(reset_token, name)
            plain_content = self._create_reset_plain_template(reset_token, name)

            return self._send_smtp_email(email, subject, html_content, plain_content)

        except Exception as e:
            logger.error(f"Excepción enviando email reset: {str(e)}")
            return False

    def send_welcome_email(
        self,
        email: str,
        user_name: str,
        user_type: str
    ) -> bool:
        """
        Envía email de bienvenida al registrarse.

        Args:
            email: Email destino
            user_name: Nombre del usuario
            user_type: Tipo de usuario (BUYER, VENDOR, etc.)

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            if self.simulation_mode:
                logger.info(f"SIMULACIÓN EMAIL BIENVENIDA - Para: {email}, Usuario: {user_name}")
                print(f"🎉 SIMULACIÓN EMAIL BIENVENIDA:")
                print(f"   Para: {email}")
                print(f"   Usuario: {user_name}")
                print(f"   Tipo: {user_type}")
                return True

            subject = "¡Bienvenido a MeStore! 🎉"

            html_content = self._create_welcome_html_template(user_name, user_type)
            plain_content = self._create_welcome_plain_template(user_name, user_type)

            return self._send_smtp_email(email, subject, html_content, plain_content)

        except Exception as e:
            logger.error(f"Excepción enviando email bienvenida: {str(e)}")
            return False

    def _create_otp_html_template(self, otp_code: str, user_name: str) -> str:
        """Crear template HTML para email OTP."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Código de Verificación - MeStore</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🛒 MeStore</h1>
                <p style="color: white; margin: 10px 0 0 0; opacity: 0.9;">Tu marketplace digital</p>
            </div>

            <div style="background: white; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-top: 0;">¡Hola {user_name}! 👋</h2>

                <p>Gracias por registrarte en MeStore. Para completar tu registro, usa este código de verificación:</p>

                <div style="background: #f8f9fa; border: 2px dashed #667eea; border-radius: 10px; padding: 30px; text-align: center; margin: 30px 0;">
                    <div style="font-size: 36px; font-weight: bold; color: #667eea; letter-spacing: 8px; font-family: monospace;">
                        {otp_code}
                    </div>
                    <p style="color: #666; margin: 15px 0 0 0; font-size: 14px;">
                        Este código expira en 10 minutos
                    </p>
                </div>

                <p style="color: #666; font-size: 14px; border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px;">
                    Si no solicitaste este código, puedes ignorar este email de forma segura.
                </p>

                <div style="text-align: center; margin-top: 30px;">
                    <p style="color: #667eea; font-weight: bold;">¡Gracias por elegir MeStore!</p>
                    <a href="{self.config.FRONTEND_URL}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 15px;">
                        Ir a MeStore
                    </a>
                </div>
            </div>
        </body>
        </html>
        """

    def _create_otp_plain_template(self, otp_code: str, user_name: str) -> str:
        """Crear template texto plano para email OTP."""
        return f"""
        ¡Hola {user_name}!

        Gracias por registrarte en MeStore.

        Tu código de verificación es: {otp_code}

        Este código expira en 10 minutos.

        Si no solicitaste este código, puedes ignorar este email.

        ¡Gracias por elegir MeStore!

        Visita: {self.config.FRONTEND_URL}
        """

    def _create_reset_html_template(self, reset_token: str, user_name: str) -> str:
        """Crear template HTML para email de reset."""
        reset_url = f"{self.config.FRONTEND_URL}/reset-password?token={reset_token}"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Recuperar Contraseña - MeStore</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🛒 MeStore</h1>
                <p style="color: white; margin: 10px 0 0 0; opacity: 0.9;">Recuperación de Contraseña</p>
            </div>

            <div style="background: white; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-top: 0;">¡Hola {user_name}! 🔐</h2>

                <p>Recibimos una solicitud para restablecer tu contraseña. Haz clic en el botón de abajo para crear una nueva contraseña:</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Restablecer Contraseña
                    </a>
                </div>

                <p style="color: #666; font-size: 14px;">
                    O copia y pega este enlace en tu navegador:<br>
                    <a href="{reset_url}" style="color: #667eea; word-break: break-all;">{reset_url}</a>
                </p>

                <p style="color: #666; font-size: 14px; border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px;">
                    Este enlace expira en 1 hora por seguridad.<br>
                    Si no solicitaste cambiar tu contraseña, puedes ignorar este email.
                </p>
            </div>
        </body>
        </html>
        """

    def _create_reset_plain_template(self, reset_token: str, user_name: str) -> str:
        """Crear template texto plano para email de reset."""
        reset_url = f"{self.config.FRONTEND_URL}/reset-password?token={reset_token}"

        return f"""
        ¡Hola {user_name}!

        Recibimos una solicitud para restablecer tu contraseña.

        Para crear una nueva contraseña, visita este enlace:
        {reset_url}

        Este enlace expira en 1 hora por seguridad.

        Si no solicitaste cambiar tu contraseña, puedes ignorar este email.

        Saludos,
        El equipo de MeStore
        """

    def _create_welcome_html_template(self, user_name: str, user_type: str) -> str:
        """Crear template HTML para email de bienvenida."""
        user_type_text = {
            'BUYER': 'Comprador',
            'VENDOR': 'Vendedor',
            'ADMIN': 'Administrador'
        }.get(user_type, user_type)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>¡Bienvenido a MeStore!</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🛒 MeStore</h1>
                <p style="color: white; margin: 10px 0 0 0; opacity: 0.9;">¡Bienvenido a tu marketplace!</p>
            </div>

            <div style="background: white; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-top: 0;">¡Hola {user_name}! 🎉</h2>

                <p>¡Bienvenido a MeStore! Tu cuenta como <strong>{user_type_text}</strong> ha sido creada exitosamente.</p>

                <div style="background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; margin: 30px 0;">
                    <h3 style="margin-top: 0; color: #667eea;">¿Qué sigue?</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Explora nuestro marketplace</li>
                        <li>Completa tu perfil</li>
                        <li>Comienza a {'vender' if user_type == 'VENDOR' else 'comprar'} productos</li>
                    </ul>
                </div>

                <div style="text-align: center; margin-top: 30px;">
                    <a href="{self.config.FRONTEND_URL}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Comenzar Ahora
                    </a>
                </div>

                <p style="color: #666; font-size: 14px; border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px;">
                    ¡Gracias por unirte a MeStore! Si tienes preguntas, no dudes en contactarnos.
                </p>
            </div>
        </body>
        </html>
        """

    def _create_welcome_plain_template(self, user_name: str, user_type: str) -> str:
        """Crear template texto plano para email de bienvenida."""
        user_type_text = {
            'BUYER': 'Comprador',
            'VENDOR': 'Vendedor',
            'ADMIN': 'Administrador'
        }.get(user_type, user_type)

        return f"""
        ¡Hola {user_name}!

        ¡Bienvenido a MeStore! Tu cuenta como {user_type_text} ha sido creada exitosamente.

        ¿Qué sigue?
        - Explora nuestro marketplace
        - Completa tu perfil
        - Comienza a {'vender' if user_type == 'VENDOR' else 'comprar'} productos

        Visita MeStore: {self.config.FRONTEND_URL}

        ¡Gracias por unirte a MeStore!

        Saludos,
        El equipo de MeStore
        """


# Instancia global del servicio
smtp_email_service = SMTPEmailService()