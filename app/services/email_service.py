# ~/app/services/email_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio Email
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Servicio Email para MeStore.

Este módulo maneja el envío de emails:
- Emails de verificación con códigos OTP
- Templates HTML para emails atractivos
- Configuración SendGrid
- Manejo de errores de envío
"""

import os
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent, PlainTextContent
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
