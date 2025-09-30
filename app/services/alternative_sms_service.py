# ~/app/services/alternative_sms_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio SMS Alternativo sin Twilio
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Servicio SMS alternativo para MeStore sin depender de Twilio.

Este módulo implementa múltiples proveedores de SMS:
- TextBelt API (gratuito con límites)
- SMS77 (económico)
- ClickSend (económico)
- Modo desarrollo con logs
"""

import os
import aiohttp
import asyncio
import logging
import re
from typing import Optional, Dict, Tuple, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class AlternativeSMSService:
    """Servicio SMS con múltiples proveedores alternativos a Twilio."""

    def __init__(self):
        """Inicializar servicio SMS con múltiples proveedores."""
        from app.core.config import settings

        self.development_mode = settings.ENVIRONMENT == 'development'
        self.sms_enabled = getattr(settings, 'SMS_ENABLED', True)

        # Configuración de proveedores
        self.providers = {
            'textbelt': {
                'enabled': True,
                'url': 'https://textbelt.com/text',
                'free_quota': 1,  # 1 SMS gratis por día
                'api_key': os.getenv('TEXTBELT_API_KEY', 'textbelt'),  # 'textbelt' para modo gratuito
                'cost': 'Gratis (1/día), después $0.01 USD/SMS'
            },
            'sms77': {
                'enabled': False,
                'url': 'https://gateway.sms77.io/api/sms',
                'api_key': os.getenv('SMS77_API_KEY', ''),
                'cost': '~€0.075/SMS'
            },
            'clicksend': {
                'enabled': False,
                'url': 'https://rest.clicksend.com/v3/sms/send',
                'username': os.getenv('CLICKSEND_USERNAME', ''),
                'api_key': os.getenv('CLICKSEND_API_KEY', ''),
                'cost': '~$0.15 USD/SMS'
            }
        }

        logger.info(f"Alternative SMS Service inicializado. Development: {self.development_mode}")

    def _format_international_phone(self, phone_number: str) -> Optional[str]:
        """
        Formatea número telefónico internacional.

        Args:
            phone_number: Número en cualquier formato

        Returns:
            Optional[str]: Número formateado o None si es inválido
        """
        if not phone_number:
            return None

        # Limpiar número (solo dígitos)
        clean_number = re.sub(r'\D', '', phone_number)

        # Si el número ya tiene + al inicio, verificar formato
        if phone_number.startswith('+'):
            if re.match(r'^\+\d{10,15}$', phone_number):
                return phone_number

        # Colombia (+57)
        if len(clean_number) == 10 and clean_number.startswith('3'):
            return f"+57{clean_number}"
        elif len(clean_number) == 12 and clean_number.startswith('57'):
            return f"+{clean_number}"

        # Estados Unidos (+1)
        elif len(clean_number) == 10 and clean_number[0] in '23456789':
            return f"+1{clean_number}"
        elif len(clean_number) == 11 and clean_number.startswith('1'):
            return f"+{clean_number}"

        logger.warning(f"Formato de teléfono no reconocido: {phone_number}")
        return None

    async def _send_textbelt_sms(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """
        Envía SMS usando TextBelt API (gratuito con límites).

        Args:
            phone_number: Número de teléfono
            message: Mensaje a enviar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            provider = self.providers['textbelt']

            payload = {
                'phone': phone_number,
                'message': message,
                'key': provider['api_key']
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(provider['url'], data=payload) as response:
                    result = await response.json()

                    if response.status == 200 and result.get('success'):
                        quota_remaining = result.get('quotaRemaining', 0)
                        logger.info(f"TextBelt SMS enviado exitosamente. Quota restante: {quota_remaining}")
                        return True, f"SMS enviado via TextBelt. Quota restante: {quota_remaining}"
                    else:
                        error_msg = result.get('error', 'Error desconocido')
                        logger.error(f"Error TextBelt: {error_msg}")
                        return False, f"Error TextBelt: {error_msg}"

        except Exception as e:
            logger.error(f"Excepción en TextBelt SMS: {str(e)}")
            return False, f"Error interno TextBelt: {str(e)}"

    async def _send_sms77_sms(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """
        Envía SMS usando SMS77 API.

        Args:
            phone_number: Número de teléfono
            message: Mensaje a enviar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            provider = self.providers['sms77']

            if not provider['api_key']:
                return False, "SMS77 API key no configurada"

            payload = {
                'to': phone_number,
                'text': message,
                'from': 'MeStore',
                'p': provider['api_key']
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(provider['url'], data=payload) as response:
                    result = await response.text()

                    if response.status == 200 and result.isdigit() and int(result) > 0:
                        logger.info(f"SMS77 SMS enviado exitosamente. ID: {result}")
                        return True, f"SMS enviado via SMS77. ID: {result}"
                    else:
                        logger.error(f"Error SMS77: {result}")
                        return False, f"Error SMS77: {result}"

        except Exception as e:
            logger.error(f"Excepción en SMS77 SMS: {str(e)}")
            return False, f"Error interno SMS77: {str(e)}"

    async def _send_clicksend_sms(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """
        Envía SMS usando ClickSend API.

        Args:
            phone_number: Número de teléfono
            message: Mensaje a enviar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            provider = self.providers['clicksend']

            if not provider['username'] or not provider['api_key']:
                return False, "ClickSend credenciales no configuradas"

            payload = {
                "messages": [
                    {
                        "source": "sdk",
                        "body": message,
                        "to": phone_number,
                        "from": "MeStore"
                    }
                ]
            }

            # Basic Auth para ClickSend
            import base64
            auth_string = f"{provider['username']}:{provider['api_key']}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(provider['url'], json=payload, headers=headers) as response:
                    result = await response.json()

                    if response.status == 200:
                        messages = result.get('data', {}).get('messages', [])
                        if messages and messages[0].get('status') == 'SUCCESS':
                            msg_id = messages[0].get('message_id')
                            logger.info(f"ClickSend SMS enviado exitosamente. ID: {msg_id}")
                            return True, f"SMS enviado via ClickSend. ID: {msg_id}"

                    error_msg = result.get('response_msg', 'Error desconocido')
                    logger.error(f"Error ClickSend: {error_msg}")
                    return False, f"Error ClickSend: {error_msg}"

        except Exception as e:
            logger.error(f"Excepción en ClickSend SMS: {str(e)}")
            return False, f"Error interno ClickSend: {str(e)}"

    async def send_otp_sms(
        self,
        phone_number: str,
        otp_code: str,
        user_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Envía SMS con código OTP usando el mejor proveedor disponible.

        Args:
            phone_number: Número de teléfono destino
            otp_code: Código OTP de 6 dígitos
            user_name: Nombre del usuario (opcional)

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            if not self.sms_enabled:
                return False, "Servicio SMS deshabilitado"

            # Formatear número telefónico
            formatted_number = self._format_international_phone(phone_number)
            if not formatted_number:
                logger.error(f"Número telefónico inválido: {phone_number}")
                return False, "Número telefónico inválido"

            # Crear mensaje SMS
            if user_name:
                message = f"MeStore: Hola {user_name}, tu código de verificación es {otp_code}. Válido por 10 minutos."
            else:
                message = f"MeStore: Tu código de verificación es {otp_code}. Válido por 10 minutos."

            # Modo desarrollo: solo simular
            if self.development_mode:
                logger.info(f"DESARROLLO SMS - Para: {formatted_number}, OTP: {otp_code}")
                print(f"📱 DESARROLLO SMS OTP:")
                print(f"   Para: {formatted_number}")
                print(f"   Código: {otp_code}")
                print(f"   Usuario: {user_name}")
                print(f"   Mensaje: {message}")
                print(f"   Timestamp: {datetime.now()}")
                return True, f"SMS simulado enviado a {formatted_number}"

            # Probar proveedores en orden de preferencia
            providers_to_try = [
                ('textbelt', self._send_textbelt_sms),
                ('sms77', self._send_sms77_sms),
                ('clicksend', self._send_clicksend_sms)
            ]

            last_error = "No hay proveedores disponibles"

            for provider_name, send_function in providers_to_try:
                if not self.providers[provider_name]['enabled']:
                    continue

                logger.info(f"Intentando enviar SMS via {provider_name}")
                success, message_result = await send_function(formatted_number, message)

                if success:
                    return True, message_result
                else:
                    last_error = message_result
                    logger.warning(f"Proveedor {provider_name} falló: {message_result}")

            # Si ningún proveedor funcionó
            logger.error(f"Todos los proveedores SMS fallaron. Último error: {last_error}")
            return False, f"Error enviando SMS: {last_error}"

        except Exception as e:
            logger.error(f"Excepción enviando SMS OTP: {str(e)}")
            return False, f"Error interno enviando SMS: {str(e)}"

    def get_service_status(self) -> Dict[str, any]:
        """
        Obtiene el estado del servicio SMS alternativo.

        Returns:
            Dict: Estado del servicio
        """
        status = {
            "service_enabled": self.sms_enabled,
            "development_mode": self.development_mode,
            "providers": {}
        }

        for name, config in self.providers.items():
            provider_status = {
                "enabled": config['enabled'],
                "cost": config['cost'],
                "configured": False
            }

            if name == 'textbelt':
                provider_status["configured"] = True  # Siempre disponible
                provider_status["note"] = "Gratuito: 1 SMS/día, después $0.01/SMS"
            elif name == 'sms77':
                provider_status["configured"] = bool(config['api_key'])
            elif name == 'clicksend':
                provider_status["configured"] = bool(config['username'] and config['api_key'])

            status["providers"][name] = provider_status

        return status

    def get_setup_instructions(self) -> Dict[str, str]:
        """
        Obtiene instrucciones de configuración para cada proveedor.

        Returns:
            Dict: Instrucciones de configuración
        """
        return {
            "textbelt": (
                "TextBelt (Gratuito/Básico):\n"
                "1. Gratis: 1 SMS por día automáticamente\n"
                "2. Pagado: Compra créditos en https://textbelt.com\n"
                "3. Agrega TEXTBELT_API_KEY=tu_key al .env"
            ),
            "sms77": (
                "SMS77 (Económico):\n"
                "1. Regístrate en https://sms77.io\n"
                "2. Obtén tu API key\n"
                "3. Agrega SMS77_API_KEY=tu_key al .env\n"
                "4. Habilita el proveedor en el código"
            ),
            "clicksend": (
                "ClickSend (Confiable):\n"
                "1. Regístrate en https://clicksend.com\n"
                "2. Obtén username y API key\n"
                "3. Agrega CLICKSEND_USERNAME y CLICKSEND_API_KEY al .env\n"
                "4. Habilita el proveedor en el código"
            )
        }


# Instancia global del servicio
alternative_sms_service = AlternativeSMSService()