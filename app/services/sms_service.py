# ~/app/services/sms_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio SMS
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Servicio SMS para MeStore.

Este módulo maneja el envío de SMS:
- SMS de verificación con códigos OTP
- Configuración Twilio
- Formateo de números telefónicos colombianos
- Manejo de errores de envío
"""

import os
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging
import re

logger = logging.getLogger(__name__)


class SMSService:
    """Servicio para envío de SMS usando Twilio."""
    
    def __init__(self):
        """Inicializar servicio SMS con configuración Twilio."""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_FROM_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning("Credenciales Twilio no configuradas. SMS service en modo simulación")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            self.client = Client(self.account_sid, self.auth_token)
    
    def send_otp_sms(
        self, 
        phone_number: str, 
        otp_code: str, 
        user_name: Optional[str] = None
    ) -> bool:
        """
        Envía SMS con código OTP de verificación.
        
        Args:
            phone_number: Número de teléfono destino
            otp_code: Código OTP de 6 dígitos
            user_name: Nombre del usuario (opcional)
            
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # Formatear número telefónico
            formatted_number = self._format_colombian_phone(phone_number)
            if not formatted_number:
                logger.error(f"Número telefónico inválido: {phone_number}")
                return False
            
            # Crear mensaje SMS
            message_body = self._create_otp_sms_template(
                otp_code=otp_code,
                user_name=user_name
            )
            
            if self.simulation_mode:
                logger.info(f"SIMULACIÓN SMS - Para: {formatted_number}, OTP: {otp_code}")
                print(f"📱 SIMULACIÓN SMS OTP:")
                print(f"   Para: {formatted_number}")
                print(f"   Código: {otp_code}")
                print(f"   Usuario: {user_name}")
                print(f"   Mensaje: {message_body}")
                return True
            
            # Enviar SMS real
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=formatted_number
            )
            
            logger.info(f"SMS OTP enviado exitosamente. SID: {message.sid}")
            return True
            
        except TwilioException as e:
            logger.error(f"Error Twilio enviando SMS OTP: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Excepción enviando SMS OTP: {str(e)}")
            return False
    
    def _format_colombian_phone(self, phone_number: str) -> Optional[str]:
        """
        Formatea número telefónico colombiano al formato internacional.
        
        Args:
            phone_number: Número en cualquier formato
            
        Returns:
            Optional[str]: Número formateado o None si es inválido
        """
        # Limpiar número (solo dígitos)
        clean_number = re.sub(r'\D', '', phone_number)
        
        # Casos colombianos comunes
        if len(clean_number) == 10 and clean_number.startswith('3'):
            # Celular: 3001234567 -> +573001234567
            return f"+57{clean_number}"
        elif len(clean_number) == 13 and clean_number.startswith('573'):
            # Ya tiene código país: 573001234567 -> +573001234567
            return f"+{clean_number}"
        elif len(clean_number) == 10 and not clean_number.startswith('3'):
            # Fijo: 6012345678 -> +576012345678
            return f"+57{clean_number}"
        elif len(clean_number) == 11 and clean_number.startswith('57'):
            # Código país sin +: 573001234567 -> +573001234567
            return f"+{clean_number}"
        
        # Formato no reconocido
        logger.warning(f"Formato de teléfono no reconocido: {phone_number}")
        return None
    
    def _create_otp_sms_template(
        self, 
        otp_code: str, 
        user_name: Optional[str] = None
    ) -> str:
        """
        Crea template para SMS OTP.
        
        Args:
            otp_code: Código OTP
            user_name: Nombre del usuario
            
        Returns:
            str: Mensaje SMS formateado
        """
        if user_name:
            return f"MeStore: Hola {user_name}, tu código de verificación es {otp_code}. Válido por 10 minutos. No compartir."
        else:
            return f"MeStore: Tu código de verificación es {otp_code}. Válido por 10 minutos. No compartir."
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Valida si un número telefónico tiene formato correcto.
        
        Args:
            phone_number: Número a validar
            
        Returns:
            bool: True si es válido
        """
        return self._format_colombian_phone(phone_number) is not None
