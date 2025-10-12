"""
Funciones auxiliares para autenticación y registro de usuarios.
"""

import random
import logging
from typing import Optional
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


def generate_verification_code() -> str:
    """
    Genera código de verificación de 6 dígitos.

    Returns:
        str: Código de 6 dígitos numéricos

    Example:
        >>> code = generate_verification_code()
        >>> print(code)
        '123456'
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


async def send_verification_email(email: str, token: str, name: Optional[str] = None, verification_link: Optional[str] = None) -> bool:
    """
    Envía email con link de verificación.

    Args:
        email: Email del destinatario
        token: Token de verificación único
        name: Nombre del usuario (opcional)
        verification_link: Link completo de verificación (opcional)

    Returns:
        bool: True si se envió exitosamente

    Example:
        >>> await send_verification_email("user@example.com", "token123", "Juan", "https://example.com/verify?token=...")
    """
    try:
        email_service = EmailService()

        subject = "Verifica tu cuenta - MeStocker"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #f7fafc;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button-box {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .verify-button {{
                    display: inline-block;
                    padding: 16px 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 18px;
                    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
                }}
                .link-box {{
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    word-break: break-all;
                    font-size: 12px;
                    color: #718096;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #718096;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔐 Verificación de Cuenta</h1>
            </div>
            <div class="content">
                <p>Hola {name or 'Usuario'},</p>

                <p>Gracias por registrarte en <strong>MeStocker</strong>. Para completar tu registro y verificar tu correo electrónico, por favor haz clic en el siguiente botón:</p>

                <div class="button-box">
                    <a href="{verification_link}" class="verify-button">✅ Verificar Email</a>
                </div>

                <p style="text-align: center; color: #718096; font-size: 14px;">
                    Este enlace es válido por <strong>24 horas</strong>
                </p>

                <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                <div class="link-box">
                    {verification_link}
                </div>

                <p><strong>¿No solicitaste esta verificación?</strong><br>
                Si no creaste una cuenta en MeStocker, puedes ignorar este correo de forma segura.</p>

                <p>Saludos,<br>
                <strong>El equipo de MeStocker</strong></p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                <p>&copy; 2025 MeStocker. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        """

        # Enviar email usando el servicio de email
        result = await email_service.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content
        )

        if result:
            logger.info(f"✅ Verification email with link sent to {email}")
        return result

    except Exception as e:
        logger.error(f"❌ Error sending verification email to {email}: {str(e)}")
        return False


async def send_welcome_email(email: str, name: Optional[str] = None) -> bool:
    """
    Envía email de bienvenida después del registro.

    Args:
        email: Email del destinatario
        name: Nombre del usuario (opcional)

    Returns:
        bool: True si se envió exitosamente

    Example:
        >>> await send_welcome_email("user@example.com", "Juan")
    """
    try:
        email_service = EmailService()

        subject = "¡Bienvenido a MeStocker! 🎉"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #f7fafc;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .feature-list {{
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .feature-item {{
                    padding: 10px 0;
                    border-bottom: 1px solid #e2e8f0;
                }}
                .feature-item:last-child {{
                    border-bottom: none;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #718096;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 ¡Bienvenido a MeStocker!</h1>
            </div>
            <div class="content">
                <p>Hola {name or 'Usuario'},</p>

                <p>¡Estamos emocionados de tenerte en nuestra comunidad! Tu cuenta ha sido creada exitosamente.</p>

                <div class="feature-list">
                    <div class="feature-item">
                        <strong>📦 Compra productos</strong><br>
                        <span style="color: #718096;">Encuentra los mejores productos de vendedores locales</span>
                    </div>
                    <div class="feature-item">
                        <strong>🏪 Conviértete en vendedor</strong><br>
                        <span style="color: #718096;">Empieza a vender tus productos en nuestra plataforma</span>
                    </div>
                    <div class="feature-item">
                        <strong>🔐 Seguridad garantizada</strong><br>
                        <span style="color: #718096;">Tus datos y transacciones están protegidos</span>
                    </div>
                </div>

                <p><strong>Próximos pasos:</strong></p>
                <ol>
                    <li>Verifica tu correo electrónico con el código que te enviamos</li>
                    <li>Verifica tu número de teléfono</li>
                    <li>Completa tu perfil</li>
                    <li>¡Empieza a comprar o vender!</li>
                </ol>

                <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>

                <p>Saludos,<br>
                <strong>El equipo de MeStocker</strong></p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                <p>&copy; 2025 MeStocker. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        """

        # Usar send_welcome_email que es el método correcto en EmailService
        result = await email_service.send_welcome_email(
            to_email=email,
            user_name=name or "Usuario"
        )

        if result:
            logger.info(f"✅ Welcome email sent to {email}")
        return result

    except Exception as e:
        logger.error(f"❌ Error sending welcome email to {email}: {str(e)}")
        return False
