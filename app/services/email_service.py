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
import html  # Python stdlib for HTML escaping to prevent XSS

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

        # Detailed diagnostic logging
        logger.info(f"🔍 EmailService Initialization Diagnostics:")
        logger.info(f"   - RESEND_AVAILABLE: {RESEND_AVAILABLE}")
        logger.info(f"   - RESEND_API_KEY configured: {bool(self.api_key)}")
        logger.info(f"   - API Key length: {len(self.api_key) if self.api_key else 0}")
        logger.info(f"   - FROM_EMAIL: {self.from_email}")
        logger.info(f"   - FROM_NAME: {self.from_name}")

        if not self.api_key or not RESEND_AVAILABLE:
            if not self.api_key:
                logger.error("❌ RESEND_API_KEY no configurado. Email service en modo simulación")
            if not RESEND_AVAILABLE:
                logger.error("❌ Resend library not installed. Email service en modo simulación")
            self.simulation_mode = True
            logger.warning("⚠️  EmailService running in SIMULATION MODE - no real emails will be sent")
        else:
            self.simulation_mode = False
            resend.api_key = self.api_key
            logger.info(f"✅ EmailService initialized successfully with Resend API")

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

            logger.info(f"📧 Attempting to send password reset email to: {to_email}")
            logger.info(f"   - Simulation mode: {self.simulation_mode}")
            logger.info(f"   - User name: {name}")
            logger.info(f"   - Token length: {len(reset_token)}")

            if self.simulation_mode:
                logger.warning(f"⚠️  SIMULACIÓN EMAIL RESET - Para: {to_email}, Token: {reset_token}")
                print(f"\n{'='*80}")
                print(f"📧 SIMULACIÓN EMAIL RESET (NO REAL EMAIL SENT):")
                print(f"   Para: {to_email}")
                print(f"   Token: {reset_token}")
                print(f"   Usuario: {name}")
                print(f"   Enlace: {self.config.FRONTEND_URL}/admin-login/reset-password?token={reset_token}")
                print(f"{'='*80}\n")
                logger.error("❌ Email NOT sent - running in simulation mode. Configure RESEND_API_KEY in Railway!")
                return True

            # Enviar con Resend
            logger.info(f"✉️  Sending real email via Resend API...")
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }

            response = resend.Emails.send(params)
            logger.info(f"✅ Password reset email sent successfully!")
            logger.info(f"   - Resend ID: {response.get('id')}")
            logger.info(f"   - To: {to_email}")
            logger.info(f"   - Subject: {subject}")
            return True

        except Exception as e:
            logger.error(f"❌ Error enviando email de reset: {str(e)}")
            logger.error(f"   - Exception type: {type(e).__name__}")
            logger.error(f"   - To email: {to_email}")
            import traceback
            logger.error(f"   - Traceback: {traceback.format_exc()}")
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

    async def send_approval_email(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """
        Envía email de aprobación de cuenta de vendedor.

        Args:
            to_email: Email del vendedor
            user_name: Nombre del vendedor

        Returns:
            bool: True si se envió exitosamente

        Security:
            user_name is HTML-escaped to prevent XSS attacks in email clients.
        """
        try:
            subject = "¡Tu cuenta de vendedor ha sido aprobada! - MeStocker"

            # 🔒 SECURITY: Sanitize user name to prevent XSS in email HTML
            safe_user_name = html.escape(user_name)

            html_content = self._create_approval_html_template(safe_user_name)

            if self.simulation_mode:
                logger.info(f"SIMULACIÓN EMAIL APROBACIÓN - Para: {to_email}")
                print(f"📧 SIMULACIÓN EMAIL APROBACIÓN:")
                print(f"   Para: {to_email}")
                print(f"   Usuario: {user_name}")
                return True

            # Enviar con Resend
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }

            response = resend.Emails.send(params)
            logger.info(f"Email de aprobación enviado. ID: {response.get('id')}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email de aprobación: {str(e)}")
            return False

    async def send_rejection_email(
        self,
        to_email: str,
        user_name: str,
        rejection_reason: str
    ) -> bool:
        """
        Envía email de rechazo de cuenta de vendedor con razón.

        Args:
            to_email: Email del vendedor
            user_name: Nombre del vendedor
            rejection_reason: Razón del rechazo

        Returns:
            bool: True si se envió exitosamente

        Security:
            Both user_name and rejection_reason are HTML-escaped to prevent XSS
            attacks in email clients.
        """
        try:
            subject = "Actualización de tu solicitud de vendedor - MeStocker"

            # 🔒 SECURITY: Sanitize user inputs to prevent XSS in email HTML
            safe_user_name = html.escape(user_name)
            safe_rejection_reason = html.escape(rejection_reason)

            html_content = self._create_rejection_html_template(safe_user_name, safe_rejection_reason)

            if self.simulation_mode:
                logger.info(f"SIMULACIÓN EMAIL RECHAZO - Para: {to_email}")
                print(f"📧 SIMULACIÓN EMAIL RECHAZO:")
                print(f"   Para: {to_email}")
                print(f"   Usuario: {user_name}")
                print(f"   Razón: {rejection_reason}")
                return True

            # Enviar con Resend
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }

            response = resend.Emails.send(params)
            logger.info(f"Email de rechazo enviado. ID: {response.get('id')}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email de rechazo: {str(e)}")
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

    def _create_approval_html_template(self, user_name: str) -> str:
        """
        Template HTML para email de aprobación de vendedor.

        Args:
            user_name: Name of the approved vendor (MUST BE HTML-ESCAPED before calling)

        Returns:
            Professional HTML email with approval notification

        Security:
            user_name should be pre-sanitized with html.escape()
            to prevent XSS attacks in email clients.
        """
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cuenta Aprobada - MeStocker</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f5f7fa;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 40px; text-align: center; border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 36px; font-weight: 700;">¡Felicidades! 🎉</h1>
                            <p style="margin: 10px 0 0; color: #d1fae5; font-size: 18px;">Tu cuenta ha sido aprobada</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px; font-size: 16px; color: #374151;">Hola <strong>{user_name}</strong>,</p>
                            <p style="margin: 0 0 30px; font-size: 16px; color: #374151; line-height: 1.6;">
                                ¡Excelentes noticias! Tu solicitud para vender en MeStocker ha sido aprobada.
                            </p>
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 30px 0;">
                                <tr>
                                    <td style="background-color: #d1fae5; border-left: 4px solid #10b981; padding: 16px; border-radius: 8px;">
                                        <p style="margin: 0; font-size: 14px; color: #065f46;">
                                            <strong>✅ Ya puedes:</strong>
                                        </p>
                                        <ul style="margin: 10px 0 0; padding-left: 20px; color: #065f46;">
                                            <li>Publicar tus productos</li>
                                            <li>Gestionar tu inventario</li>
                                            <li>Recibir pedidos</li>
                                            <li>Acceder a tu dashboard de vendedor</li>
                                        </ul>
                                    </td>
                                </tr>
                            </table>
                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="text-align: center; padding: 20px 0;">
                                        <a href="{self.config.FRONTEND_URL}/seller/dashboard"
                                           style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                                                  color: #ffffff; padding: 16px 40px; text-decoration: none;
                                                  border-radius: 8px; font-weight: 600; font-size: 16px;">
                                            Ir a Mi Dashboard
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-radius: 0 0 12px 12px;">
                            <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                                © 2025 MeStocker - Tu plataforma de ventas
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    def _create_rejection_html_template(self, user_name: str, rejection_reason: str) -> str:
        """
        Template HTML para email de rechazo de vendedor.

        Args:
            user_name: Name of the rejected vendor (MUST BE HTML-ESCAPED before calling)
            rejection_reason: Reason for rejection (MUST BE HTML-ESCAPED before calling)

        Returns:
            Professional HTML email with rejection details

        Security:
            Both user_name and rejection_reason should be pre-sanitized with html.escape()
            to prevent XSS attacks in email clients.
        """
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Actualización de Solicitud - MeStocker</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f5f7fa;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 40px; text-align: center; border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">Actualización de tu Solicitud</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px; font-size: 16px; color: #374151;">Hola <strong>{user_name}</strong>,</p>
                            <p style="margin: 0 0 30px; font-size: 16px; color: #374151; line-height: 1.6;">
                                Gracias por tu interés en vender en MeStocker. Lamentablemente, no hemos podido aprobar tu solicitud en este momento.
                            </p>
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 30px 0;">
                                <tr>
                                    <td style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 8px;">
                                        <p style="margin: 0; font-size: 14px; color: #92400e;">
                                            <strong>📋 Razón:</strong>
                                        </p>
                                        <p style="margin: 10px 0 0; font-size: 14px; color: #92400e; line-height: 1.6;">
                                            {rejection_reason}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin: 20px 0; font-size: 16px; color: #374151; line-height: 1.6;">
                                Puedes corregir la información y volver a aplicar cuando estés listo.
                            </p>
                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="text-align: center; padding: 20px 0;">
                                        <a href="{self.config.FRONTEND_URL}/register"
                                           style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                                  color: #ffffff; padding: 16px 40px; text-decoration: none;
                                                  border-radius: 8px; font-weight: 600; font-size: 16px;">
                                            Intentar de Nuevo
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-radius: 0 0 12px 12px;">
                            <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                                © 2025 MeStocker
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
