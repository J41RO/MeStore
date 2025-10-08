# ~/app/services/email_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio Email con Resend
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Servicio Email para MeStore usando Resend.

Este módulo maneja el envío de emails:
- Emails de verificación con códigos OTP
- Emails de recuperación de contraseña
- Templates HTML para emails atractivos
- Configuración Resend
- Manejo de errores de envío
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Try to import resend, if not available use simulation mode
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    logger.warning("Resend library not installed. Email service will run in simulation mode.")


class EmailConfig:
    """PRODUCTION_READY: Configuración dinámica para emails"""

    def __init__(self):
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
        self.FRONTEND_URL = self._get_frontend_url()

    def _get_frontend_url(self) -> str:
        if self.ENVIRONMENT == 'production':
            return os.getenv('FRONTEND_URL', 'https://me-store-alpha.vercel.app')
        return os.getenv('DEV_FRONTEND_URL', 'http://192.168.1.137:5173')


class EmailService:
    """Servicio para envío de emails usando Resend."""

    def __init__(self):
        """Inicializar servicio de email con configuración."""
        self.config = EmailConfig()
        self.api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('EMAIL_FROM', 'onboarding@resend.dev')
        self.from_name = os.getenv('EMAIL_FROM_NAME', 'MeStocker')

        if not self.api_key or not RESEND_AVAILABLE:
            if not self.api_key:
                logger.warning("RESEND_API_KEY no configurado. Email service en modo simulación")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            resend.api_key = self.api_key

    async def send_otp_email(
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
            name = user_name or "Usuario"
            subject = f"MeStocker - Código de verificación: {otp_code}"
            html_content = self._create_otp_html_template(otp_code, name)

            if self.simulation_mode:
                logger.info(f"SIMULACIÓN EMAIL OTP - Para: {email}, OTP: {otp_code}")
                print(f"📧 SIMULACIÓN EMAIL OTP:")
                print(f"   Para: {email}")
                print(f"   Código: {otp_code}")
                print(f"   Usuario: {name}")
                return True

            # Enviar con Resend
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [email],
                "subject": subject,
                "html": html_content
            }

            response = resend.Emails.send(params)
            logger.info(f"Email OTP enviado exitosamente a {email}. ID: {response.get('id')}")
            return True

        except Exception as e:
            logger.error(f"Excepción enviando email OTP: {str(e)}")
            return False

    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """
        Envía email con enlace para reset de contraseña.

        Args:
            to_email: Email destino
            user_name: Nombre del usuario
            reset_token: Token de reset único

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            name = user_name or "Usuario"
            subject = "Recuperación de Contraseña - MeStocker"
            html_content = self._create_reset_html_template(reset_token, name)

            if self.simulation_mode:
                logger.info(f"SIMULACIÓN EMAIL RESET - Para: {to_email}, Token: {reset_token}")
                print(f"📧 SIMULACIÓN EMAIL RESET:")
                print(f"   Para: {to_email}")
                print(f"   Token: {reset_token}")
                print(f"   Usuario: {name}")
                print(f"   Enlace: {self.config.FRONTEND_URL}/admin-login/reset-password?token={reset_token}")
                return True

            # Enviar con Resend
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }

            response = resend.Emails.send(params)
            logger.info(f"Email reset enviado exitosamente. ID: {response.get('id')}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email de reset: {str(e)}")
            return False

    async def send_password_changed_email(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """
        Envía email de confirmación de cambio de contraseña.

        Args:
            to_email: Email destino
            user_name: Nombre del usuario

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            name = user_name or "Usuario"
            subject = "Contraseña Actualizada - MeStocker"
            html_content = self._create_password_changed_html_template(name)

            if self.simulation_mode:
                logger.info(f"SIMULACIÓN EMAIL PASSWORD CHANGED - Para: {to_email}")
                print(f"📧 SIMULACIÓN EMAIL PASSWORD CHANGED:")
                print(f"   Para: {to_email}")
                print(f"   Usuario: {name}")
                return True

            # Enviar con Resend
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }

            response = resend.Emails.send(params)
            logger.info(f"Email password changed enviado exitosamente. ID: {response.get('id')}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email de confirmación: {str(e)}")
            return False

    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """
        Envía email de bienvenida a nuevos usuarios.

        Args:
            to_email: Email destino
            user_name: Nombre del usuario

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            name = user_name or "Usuario"
            subject = "¡Bienvenido a MeStocker! 🎉"
            html_content = self._create_welcome_html_template(name)

            if self.simulation_mode:
                logger.info(f"SIMULACIÓN EMAIL WELCOME - Para: {to_email}")
                print(f"📧 SIMULACIÓN EMAIL WELCOME:")
                print(f"   Para: {to_email}")
                print(f"   Usuario: {name}")
                return True

            # Enviar con Resend
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }

            response = resend.Emails.send(params)
            logger.info(f"Email welcome enviado exitosamente. ID: {response.get('id')}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email de bienvenida: {str(e)}")
            return False

    # ============================================================================
    # EMAIL TEMPLATES
    # ============================================================================

    def _create_otp_html_template(self, otp_code: str, user_name: str) -> str:
        """Crea template HTML para email OTP."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Código de Verificación MeStocker</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f5f7fa;">
                <tr>
                    <td style="padding: 40px 20px;">
                        <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; text-align: center; border-radius: 12px 12px 0 0;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">MeStocker</h1>
                                    <p style="margin: 10px 0 0; color: #e0e7ff; font-size: 16px;">Código de Verificación</p>
                                </td>
                            </tr>

                            <!-- Body -->
                            <tr>
                                <td style="padding: 40px 40px 30px;">
                                    <p style="margin: 0 0 20px; font-size: 16px; color: #374151;">Hola <strong>{user_name}</strong>,</p>

                                    <p style="margin: 0 0 30px; font-size: 16px; color: #374151; line-height: 1.6;">
                                        Has solicitado verificar tu email en MeStocker. Usa el siguiente código de verificación:
                                    </p>

                                    <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                        <tr>
                                            <td style="text-align: center; padding: 20px 0;">
                                                <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px 40px; border-radius: 12px;">
                                                    <span style="font-size: 36px; font-weight: 700; color: #ffffff; letter-spacing: 8px;">
                                                        {otp_code}
                                                    </span>
                                                </div>
                                            </td>
                                        </tr>
                                    </table>

                                    <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 30px 0;">
                                        <tr>
                                            <td style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 8px;">
                                                <p style="margin: 0; font-size: 14px; color: #92400e;">
                                                    <strong>⏰ Importante:</strong> Este código expira en 10 minutos
                                                </p>
                                            </td>
                                        </tr>
                                    </table>

                                    <p style="margin: 0; font-size: 14px; color: #6b7280; line-height: 1.6;">
                                        Si no solicitaste este código, puedes ignorar este email con seguridad.
                                    </p>
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-radius: 0 0 12px 12px;">
                                    <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                                        © 2025 MeStocker - Tu plataforma de fulfillment inteligente
                                    </p>
                                    <p style="margin: 10px 0 0; font-size: 12px; color: #9ca3af;">
                                        Este email fue enviado automáticamente, por favor no responder.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def _create_reset_html_template(self, reset_token: str, user_name: str) -> str:
        """Crea template HTML para email de reset de contraseña."""
        reset_url = f"{self.config.FRONTEND_URL}/admin-login/reset-password?token={reset_token}"

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recuperación de Contraseña - MeStocker</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f5f7fa;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; text-align: center; border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">MeStocker</h1>
                            <p style="margin: 10px 0 0; color: #e0e7ff; font-size: 16px;">Recuperación de Contraseña</p>
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px 40px 30px;">
                            <p style="margin: 0 0 20px; font-size: 16px; color: #374151;">Hola <strong>{user_name}</strong>,</p>

                            <p style="margin: 0 0 30px; font-size: 16px; color: #374151; line-height: 1.6;">
                                Hemos recibido una solicitud para restablecer la contraseña de tu cuenta administrativa en MeStocker.
                            </p>

                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="text-align: center; padding: 20px 0;">
                                        <a href="{reset_url}"
                                           style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                                  color: #ffffff; padding: 16px 40px; text-decoration: none;
                                                  border-radius: 8px; font-weight: 600; font-size: 16px;">
                                            Restablecer Contraseña
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin: 30px 0 10px; font-size: 14px; color: #6b7280;">
                                Si no puedes hacer clic en el botón, copia y pega este enlace en tu navegador:
                            </p>
                            <p style="margin: 0; font-size: 12px; color: #9ca3af; word-break: break-all; background-color: #f9fafb; padding: 12px; border-radius: 6px;">
                                {reset_url}
                            </p>

                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 30px 0;">
                                <tr>
                                    <td style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 8px;">
                                        <p style="margin: 0; font-size: 14px; color: #92400e;">
                                            <strong>⚠️ Importante:</strong> Este enlace expira en 1 hora.
                                        </p>
                                        <p style="margin: 10px 0 0; font-size: 14px; color: #92400e;">
                                            Si no solicitaste este cambio, ignora este email.
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin: 0; font-size: 14px; color: #6b7280; line-height: 1.6;">
                                Por tu seguridad, nunca compartimos enlaces de recuperación por teléfono o redes sociales.
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-radius: 0 0 12px 12px;">
                            <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                                © 2025 MeStocker - Portal Administrativo
                            </p>
                            <p style="margin: 10px 0 0; font-size: 12px; color: #9ca3af;">
                                Bucaramanga, Colombia
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    def _create_password_changed_html_template(self, user_name: str) -> str:
        """Crea template HTML para confirmación de cambio de contraseña."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contraseña Actualizada - MeStocker</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f5f7fa;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 40px; text-align: center; border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">✓ Contraseña Actualizada</h1>
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px 40px 30px;">
                            <p style="margin: 0 0 20px; font-size: 16px; color: #374151;">Hola <strong>{user_name}</strong>,</p>

                            <p style="margin: 0 0 30px; font-size: 16px; color: #374151; line-height: 1.6;">
                                Tu contraseña ha sido actualizada exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.
                            </p>

                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 30px 0;">
                                <tr>
                                    <td style="background-color: #d1fae5; border-left: 4px solid #10b981; padding: 16px; border-radius: 8px;">
                                        <p style="margin: 0; font-size: 14px; color: #065f46;">
                                            <strong>🔒 Cuenta segura:</strong> Tu cuenta está protegida.
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 30px 0;">
                                <tr>
                                    <td style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 8px;">
                                        <p style="margin: 0; font-size: 14px; color: #92400e;">
                                            <strong>⚠️ ¿No fuiste tú?</strong>
                                        </p>
                                        <p style="margin: 10px 0 0; font-size: 14px; color: #92400e;">
                                            Si no realizaste este cambio, contacta inmediatamente a soporte@mestocker.com
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-radius: 0 0 12px 12px;">
                            <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                                © 2025 MeStocker - Portal Administrativo
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    def _create_welcome_html_template(self, user_name: str) -> str:
        """Crea template HTML para email de bienvenida."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bienvenido a MeStocker</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f5f7fa;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; text-align: center; border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 36px; font-weight: 700;">¡Bienvenido! 🎉</h1>
                            <p style="margin: 10px 0 0; color: #e0e7ff; font-size: 18px;">MeStocker</p>
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px 40px 30px;">
                            <p style="margin: 0 0 20px; font-size: 18px; color: #374151;">Hola <strong>{user_name}</strong>,</p>

                            <p style="margin: 0 0 30px; font-size: 16px; color: #374151; line-height: 1.6;">
                                ¡Gracias por unirte a MeStocker! Estamos emocionados de tenerte en nuestra plataforma de fulfillment inteligente.
                            </p>

                            <h3 style="margin: 30px 0 15px; color: #667eea; font-size: 20px;">Próximos Pasos:</h3>

                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 12px; background-color: #f9fafb; border-radius: 8px; margin-bottom: 10px;">
                                        <p style="margin: 0; font-size: 15px; color: #374151;">
                                            <strong>1.</strong> Completa tu perfil administrativo
                                        </p>
                                    </td>
                                </tr>
                                <tr><td style="height: 10px;"></td></tr>
                                <tr>
                                    <td style="padding: 12px; background-color: #f9fafb; border-radius: 8px;">
                                        <p style="margin: 0; font-size: 15px; color: #374151;">
                                            <strong>2.</strong> Explora el panel administrativo
                                        </p>
                                    </td>
                                </tr>
                                <tr><td style="height: 10px;"></td></tr>
                                <tr>
                                    <td style="padding: 12px; background-color: #f9fafb; border-radius: 8px;">
                                        <p style="margin: 0; font-size: 15px; color: #374151;">
                                            <strong>3.</strong> Configura tu equipo y permisos
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin: 30px 0 0; font-size: 14px; color: #6b7280; line-height: 1.6;">
                                Si tienes alguna pregunta, nuestro equipo de soporte está aquí para ayudarte.
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-radius: 0 0 12px 12px;">
                            <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                                © 2025 MeStocker - Fulfillment Inteligente
                            </p>
                            <p style="margin: 10px 0 0; font-size: 12px; color: #9ca3af;">
                                Bucaramanga, Colombia
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
