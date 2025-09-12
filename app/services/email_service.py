# ~/app/services/email_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio Email
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Servicio Email para MeStore.

Este módulo maneja el envío de emails:
- Emails de verificación con códigos OTP
- Emails de recuperación de contraseña
- Templates HTML para emails atractivos
- Configuración SendGrid
- Manejo de errores de envío
"""

import os
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent, PlainTextContent, Content, Email
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para envío de emails usando SendGrid."""
    
    def __init__(self):
        """Inicializar servicio de email con configuración."""
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@mestore.com')
        self.from_name = os.getenv('FROM_NAME', 'MeStore')
        
        if not self.api_key:
            logger.warning("SENDGRID_API_KEY no configurado. Email service en modo simulación")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            self.sg = SendGridAPIClient(api_key=self.api_key)
    
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
            # Preparar contenido del email
            subject_text = f"MeStore - Código de verificación: {otp_code}"
            
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
            
            if self.simulation_mode:
                logger.info(f"SIMULACIÓN EMAIL - Para: {email}, OTP: {otp_code}")
                print(f"📧 SIMULACIÓN EMAIL OTP:")
                print(f"   Para: {email}")
                print(f"   Código: {otp_code}")
                print(f"   Usuario: {user_name}")
                return True
            
            # Crear y enviar email
            message = Mail(
                from_email=From(self.from_email, self.from_name),
                to_emails=To(email),
                subject=Subject(subject_text),
                html_content=HtmlContent(html_content),
                plain_text_content=PlainTextContent(plain_content)
            )
            
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email OTP enviado exitosamente a {email}")
                return True
            else:
                logger.error(f"Error enviando email OTP: {response.status_code}")
                return False
                
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
            # Crear mensaje de email
            message = Mail()
            message.from_email = Email(self.from_email, self.from_name)
            message.to = [To(email)]
            message.subject = "Recuperación de Contraseña - MeStore"

            # Crear contenido HTML y texto plano
            name = user_name or "Usuario"
            html_content = self._create_reset_html_template(reset_token, name)
            plain_content = self._create_reset_plain_template(reset_token, name)

            message.content = [
                Content("text/plain", plain_content),
                Content("text/html", html_content)
            ]

            if self.simulation_mode:
                logger.info(f"SIMULACIÓN EMAIL RESET - Para: {email}, Token: {reset_token}")
                print(f"📧 SIMULACIÓN EMAIL RESET:")
                print(f"   Para: {email}")
                print(f"   Token: {reset_token}")
                print(f"   Usuario: {name}")
                print(f"   Enlace: http://localhost:3000/reset-password?token={reset_token}")
                return True

            # Enviar email real
            response = self.sg.send(message)
            logger.info(f"Email reset enviado exitosamente. Status: {response.status_code}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email de reset: {str(e)}")
            return False
    
    def send_lead_welcome_email(
        self,
        email: str,
        nombre: str,
        tipo_negocio: str
    ) -> bool:
        """
        Envía email de bienvenida para leads nuevos.

        Args:
            email: Email del lead
            nombre: Nombre del lead
            tipo_negocio: Tipo de negocio (vendedor/comprador/ambos)

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            subject_text = "¡Bienvenido al futuro del fulfillment! - MeStocker Early Access"
            
            # Contenido personalizado por tipo de negocio
            business_benefits = {
                'vendedor': {
                    'title': 'Para Vendedores Inteligentes',
                    'benefits': [
                        'Automatización completa de inventario 24/7',
                        'IA que optimiza tus precios automáticamente',
                        'Acceso directo a 500+ compradores activos',
                        'Reducción del 40% en costos operativos'
                    ]
                },
                'comprador': {
                    'title': 'Para Compradores Estratégicos', 
                    'benefits': [
                        'Acceso prioritario a productos exclusivos',
                        'Precios mayoristas automatizados',
                        'Fulfillment local en Bucaramanga',
                        'Análisis predictivo de stock disponible'
                    ]
                },
                'ambos': {
                    'title': 'Para Empresarios Visionarios',
                    'benefits': [
                        'Doble flujo de ingresos: compra y vende',
                        'Plataforma unificada B2B + B2C',
                        'IA especializada para ambos roles',
                        'ROI maximizado con estrategia híbrida'
                    ]
                }
            }
            
            # Contenido HTML
            html_content = self._create_lead_welcome_html_template(
                nombre=nombre,
                tipo_negocio=tipo_negocio,
                business_info=business_benefits.get(tipo_negocio, business_benefits['vendedor'])
            )
            
            # Contenido texto plano
            plain_content = self._create_lead_welcome_plain_template(
                nombre=nombre,
                tipo_negocio=tipo_negocio
            )
            
            if self.simulation_mode:
                logger.info(f"SIMULACIÓN EMAIL LEAD - Para: {email}, Lead: {nombre}")
                print(f"📧 SIMULACIÓN EMAIL LEAD WELCOME:")
                print(f"   Para: {email}")
                print(f"   Nombre: {nombre}")
                print(f"   Tipo: {tipo_negocio}")
                return True
            
            # Crear y enviar email
            message = Mail(
                from_email=From(self.from_email, "MeStocker Team"),
                to_emails=To(email),
                subject=Subject(subject_text),
                html_content=HtmlContent(html_content),
                plain_text_content=PlainTextContent(plain_content)
            )
            
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email lead welcome enviado exitosamente a {email}")
                return True
            else:
                logger.error(f"Error enviando email lead welcome: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción enviando email lead welcome: {str(e)}")
            return False
    
    def _create_otp_html_template(self, otp_code: str, user_name: str) -> str:
        """Crea template HTML para email OTP."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Código de Verificación MeStore</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                <h1 style="color: #007bff;">MeStore</h1>
                <h2 style="color: #333;">Código de Verificación</h2>
            </div>
            
            <div style="padding: 30px; background-color: white;">
                <p>Hola <strong>{user_name}</strong>,</p>
                
                <p>Has solicitado verificar tu email en MeStore. Tu código de verificación es:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <span style="font-size: 32px; font-weight: bold; color: #007bff; 
                                 letter-spacing: 8px; background-color: #f8f9fa; 
                                 padding: 15px 25px; border-radius: 8px; border: 2px solid #007bff;">
                        {otp_code}
                    </span>
                </div>
                
                <p style="color: #dc3545; font-weight: bold;">
                    ⏰ Este código expira en 10 minutos
                </p>
                
                <p>Si no solicitaste este código, puedes ignorar este email.</p>
                
                <hr style="margin: 30px 0; border: 1px solid #dee2e6;">
                
                <p style="font-size: 12px; color: #6c757d; text-align: center;">
                    MeStore - Tu marketplace de confianza<br>
                    Este email fue enviado automáticamente, no responder.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _create_otp_plain_template(self, otp_code: str, user_name: str) -> str:
        """Crea template texto plano para email OTP."""
        return f"""
MeStore - Código de Verificación

Hola {user_name},

Has solicitado verificar tu email en MeStore.

Tu código de verificación es: {otp_code}

Este código expira en 10 minutos.

Si no solicitaste este código, puedes ignorar este email.

---
MeStore - Tu marketplace de confianza
Este email fue enviado automáticamente, no responder.
        """

    def _create_reset_html_template(self, reset_token: str, user_name: str) -> str:
        """Crea template HTML para email de reset de contraseña."""
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Recuperación de Contraseña - MeStore</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
        <img src="https://mestore.com/logo.png" alt="MeStore" style="max-width: 150px;">
        <h1 style="color: #333;">Recuperación de Contraseña</h1>
    </div>
    
    <div style="padding: 30px; background-color: white;">
        <h2 style="color: #333;">Hola {user_name},</h2>
        
        <p style="font-size: 16px; line-height: 1.6; color: #555;">
            Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en MeStore.
        </p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" 
               style="background-color: #007bff; color: white; padding: 15px 30px; 
                      text-decoration: none; border-radius: 5px; font-weight: bold;
                      display: inline-block;">
                Restablecer Contraseña
            </a>
        </div>
        
        <p style="font-size: 14px; color: #666;">
            Si no puedes hacer clic en el botón, copia y pega este enlace en tu navegador:
        </p>
        <p style="font-size: 12px; color: #888; word-break: break-all;">
            {reset_url}
        </p>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; 
                   padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="color: #856404; margin: 0; font-size: 14px;">
                <strong>⚠️ Importante:</strong> Este enlace expira en 1 hora. 
                Si no solicitaste este cambio, ignora este email.
            </p>
        </div>
        
        <p style="font-size: 14px; color: #666;">
            Por tu seguridad, nunca compartimos enlaces de recuperación por teléfono o redes sociales.
        </p>
    </div>
    
    <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
        <p style="color: #888; font-size: 12px; margin: 0;">
            © 2025 MeStore. Todos los derechos reservados.
        </p>
    </div>
</body>
</html>"""

    def _create_reset_plain_template(self, reset_token: str, user_name: str) -> str:
        # Crea template texto plano para email de reset
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
        
        lines = [
            "MeStore - Recuperacion de Contrasena",
            "",
            f"Hola {user_name},",
            "",
            "Hemos recibido una solicitud para restablecer la contrasena de tu cuenta en MeStore.",
            "",
            "Para restablecer tu contrasena, haz clic en el siguiente enlace:",
            reset_url,
            "",
            "IMPORTANTE:",
            "- Este enlace expira en 1 hora",
            "- Si no solicitaste este cambio, ignora este email",
            "",
            "Saludos,",
            "Equipo MeStore",
            "",
            "2025 MeStore. Todos los derechos reservados."
        ]
        return "\n".join(lines)
    
    def _create_lead_welcome_html_template(self, nombre: str, tipo_negocio: str, business_info: dict) -> str:
        # Crea template HTML para email de bienvenida de leads
        benefits_html = "".join([f"<li>{benefit}</li>" for benefit in business_info['benefits']])
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head><meta charset='UTF-8'><title>Bienvenido a MeStocker</title></head>",
            "<body style='font-family: Arial; max-width: 600px; margin: 0 auto;'>",
            f"<div style='background: #667eea; padding: 30px; text-align: center;'>",
            f"<h1 style='color: white; margin: 0;'>MeStocker</h1>",
            f"<p style='color: white;'>El futuro del fulfillment inteligente</p>",
            "</div>",
            "<div style='padding: 30px; background: white;'>",
            f"<h2>Bienvenido, {nombre}!</h2>",
            "<p>Gracias por unirte al Early Access de MeStocker.</p>",
            f"<h3>{business_info['title']}</h3>",
            f"<ul>{benefits_html}</ul>",
            "<h3>Proximos Pasos:</h3>",
            "<p>1. Te contactaremos en 48 horas</p>",
            "<p>2. Configuracion de cuenta</p>",
            "<p>3. Acceso prioritario</p>",
            "<p>Saludos,<br>Equipo MeStocker</p>",
            "</div>",
            "<div style='background: #f8f9fa; padding: 20px; text-align: center;'>",
            "<p style='font-size: 12px;'>2025 MeStocker. Bucaramanga, Colombia.</p>",
            "</div>",
            "</body>",
            "</html>"
        ]
        
        return "\n".join(html_parts)
    
    def _create_lead_welcome_plain_template(self, nombre: str, tipo_negocio: str) -> str:
        # Crea template texto plano para email de bienvenida de leads
        lines = [
            "MeStocker - Bienvenido al Early Access!",
            "",
            f"Hola {nombre},",
            "",
            "Gracias por unirte al Early Access de MeStocker. Eres de los primeros en descubrir la plataforma de fulfillment mas avanzada de Colombia.",
            "",
            f"Como {tipo_negocio}, tendras acceso a:",
            "- Automatizacion completa de inventario 24/7",
            "- IA que optimiza precios automaticamente",
            "- Acceso a red de 500+ compradores/vendedores", 
            "- Reduccion del 40% en costos operativos",
            "",
            "PROXIMOS PASOS:",
            "1. Te contactaremos en las proximas 48 horas",
            "2. Configuracion personalizada de tu cuenta",
            "3. Acceso prioritario al beta",
            "",
            "Tienes preguntas? Responde a este email.",
            "",
            "Saludos,",
            "Equipo MeStocker",
            "Revolucionando el fulfillment en Colombia",
            "",
            "2025 MeStocker. Bucaramanga, Colombia."
        ]
        return "\n".join(lines)