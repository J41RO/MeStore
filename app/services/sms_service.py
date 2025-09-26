# ~/app/services/sms_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio SMS con Twilio
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Servicio SMS para MeStore con integración completa de Twilio.

Este módulo maneja el envío de SMS:
- SMS de verificación con códigos OTP
- Configuración completa Twilio
- Formateo de números telefónicos colombianos
- Rate limiting y control de frecuencia
- Manejo avanzado de errores
- Fallback a modo simulación en desarrollo
"""

import os
import time
from typing import Optional, Dict, Tuple
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging
import re
from datetime import datetime, timedelta
from app.core.redis import RedisService

logger = logging.getLogger(__name__)


class SMSService:
    """Servicio para envío de SMS usando Twilio con funcionalidades avanzadas."""

    def __init__(self, redis_service: Optional[RedisService] = None):
        """Inicializar servicio SMS con configuración Twilio."""
        # Import Settings here to avoid circular imports
        from app.core.config import settings

        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_FROM_NUMBER
        self.verify_service_sid = settings.TWILIO_VERIFY_SERVICE_SID

        # Rate limiting configuration
        self.rate_limit_per_number = int(os.getenv('SMS_RATE_LIMIT_PER_NUMBER', '5'))  # 5 SMS per hour per number
        self.rate_limit_window = int(os.getenv('SMS_RATE_LIMIT_WINDOW', '3600'))  # 1 hour

        # SMS configuration
        self.sms_enabled = settings.SMS_ENABLED
        self.development_mode = settings.ENVIRONMENT == 'development'

        # Redis for rate limiting
        self.redis_service = redis_service

        # Check configuration and initialize client
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning(
                "Credenciales Twilio incompletas. SMS service en modo simulación.\n"
                "Configurar: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER"
            )
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            try:
                self.client = Client(self.account_sid, self.auth_token)
                # Test connection
                if not self.development_mode:
                    self._test_twilio_connection()
                logger.info("SMS Service inicializado correctamente con Twilio")
            except Exception as e:
                logger.error(f"Error inicializando cliente Twilio: {str(e)}")
                self.simulation_mode = True
    
    def _test_twilio_connection(self) -> bool:
        """
        Testa la conexión con Twilio API.

        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            # Test with account info
            account = self.client.api.accounts(self.account_sid).fetch()
            logger.info(f"Conexión Twilio exitosa. Status: {account.status}")
            return True
        except Exception as e:
            logger.error(f"Error testando conexión Twilio: {str(e)}")
            return False

    def _check_rate_limit(self, phone_number: str) -> Tuple[bool, str]:
        """
        Verifica si el número ha excedido el rate limit.

        Args:
            phone_number: Número de teléfono a verificar

        Returns:
            Tuple[bool, str]: (permitido, mensaje)
        """
        if not self.redis_service:
            return True, "Rate limiting disabled"

        try:
            rate_limit_key = f"sms_rate_limit:{phone_number}"
            current_count = self.redis_service.get(rate_limit_key)

            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)

            if current_count >= self.rate_limit_per_number:
                return False, f"Rate limit excedido. Máximo {self.rate_limit_per_number} SMS por hora"

            return True, "Within rate limit"
        except Exception as e:
            logger.error(f"Error verificando rate limit: {str(e)}")
            return True, "Rate limit check failed, allowing"

    def _increment_rate_limit(self, phone_number: str) -> None:
        """
        Incrementa el contador de rate limiting.

        Args:
            phone_number: Número de teléfono
        """
        if not self.redis_service:
            return

        try:
            rate_limit_key = f"sms_rate_limit:{phone_number}"
            current_count = self.redis_service.get(rate_limit_key)

            if current_count is None:
                self.redis_service.setex(rate_limit_key, self.rate_limit_window, 1)
            else:
                self.redis_service.incr(rate_limit_key)
        except Exception as e:
            logger.error(f"Error incrementando rate limit: {str(e)}")

    def send_otp_sms(
        self,
        phone_number: str,
        otp_code: str,
        user_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Envía SMS con código OTP de verificación con rate limiting.

        Args:
            phone_number: Número de teléfono destino
            otp_code: Código OTP de 6 dígitos
            user_name: Nombre del usuario (opcional)

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Verificar si SMS está habilitado
            if not self.sms_enabled:
                return False, "Servicio SMS deshabilitado en configuración"

            # Formatear número telefónico (soporte internacional)
            formatted_number = self._format_international_phone(phone_number)
            if not formatted_number:
                logger.error(f"Número telefónico inválido: {phone_number}")
                return False, "Número telefónico inválido"

            # Verificar rate limiting
            rate_allowed, rate_message = self._check_rate_limit(formatted_number)
            if not rate_allowed:
                logger.warning(f"Rate limit excedido para {formatted_number}")
                return False, rate_message

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
                print(f"   Timestamp: {datetime.now()}")

                # Increment rate limit even in simulation
                self._increment_rate_limit(formatted_number)
                return True, f"SMS simulado enviado a {formatted_number}"

            # Enviar SMS real
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=formatted_number
            )

            # Increment rate limit only on successful send
            self._increment_rate_limit(formatted_number)

            logger.info(f"SMS OTP enviado exitosamente. SID: {message.sid}, Status: {message.status}")
            return True, f"SMS enviado a {formatted_number}"

        except TwilioException as e:
            error_details = self._parse_twilio_error(e)
            logger.error(f"Error Twilio enviando SMS OTP: {error_details}")
            return False, f"Error enviando SMS: {error_details}"
        except Exception as e:
            logger.error(f"Excepción enviando SMS OTP: {str(e)}")
            return False, f"Error interno enviando SMS: {str(e)}"
    
    def _format_international_phone(self, phone_number: str) -> Optional[str]:
        """
        Formatea número telefónico internacional con soporte para múltiples países.

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
            # Validar que después del + solo hay dígitos
            if re.match(r'^\+\d{10,15}$', phone_number):
                return phone_number  # Ya está en formato internacional válido

        # Números con código de país explícito primero
        if len(clean_number) == 11 and clean_number.startswith('1'):
            # 11 dígitos comenzando con 1: número US con código país
            return f"+{clean_number}"

        # Colombia (+57) - mantener compatibilidad existente (prioridad)
        if len(clean_number) == 10:
            # 10 dígitos: puede ser celular (300..., 301..., etc.) o fijo (601..., etc.)
            if clean_number.startswith('3'):
                # Celular: 3001234567 -> +573001234567
                return f"+57{clean_number}"
            elif clean_number.startswith(('1', '6', '8')):
                # Fijo colombiano específico: 1xxx, 6xxx, 8xxx
                return f"+57{clean_number}"
            # Estados Unidos (+1) - verificar area codes específicos
            elif clean_number[0] in '23456789':
                # Area codes US comunes: 201-999 (evitar 1xx y 200 que son reservados)
                # Verificar area codes válidos específicos
                us_area_codes = ['201', '202', '203', '205', '206', '207', '208', '209', '210', '212', '213', '214', '215', '216', '217', '218', '219', '224', '225', '228', '229', '231', '234', '239', '240', '248', '251', '252', '253', '254', '256', '260', '262', '267', '269', '270', '276', '281', '283', '301', '302', '303', '304', '305', '307', '308', '309', '310', '312', '313', '314', '315', '316', '317', '318', '319', '320', '321', '323', '325', '330', '331', '334', '336', '337', '339', '347', '351', '352', '360', '361', '386', '401', '402', '404', '405', '406', '407', '408', '409', '410', '412', '413', '414', '415', '417', '419', '423', '424', '425', '430', '432', '434', '435', '440', '443', '445', '458', '469', '470', '475', '478', '479', '480', '484', '501', '502', '503', '504', '505', '507', '508', '509', '510', '512', '513', '515', '516', '517', '518', '520', '530', '540', '541', '551', '559', '561', '562', '563', '564', '567', '570', '571', '573', '574', '575', '580', '585', '586', '601', '602', '603', '605', '606', '607', '608', '609', '610', '612', '614', '615', '616', '617', '618', '619', '620', '623', '626', '628', '629', '630', '631', '636', '641', '646', '650', '651', '657', '660', '661', '662', '667', '678', '682', '701', '702', '703', '704', '706', '707', '708', '712', '713', '714', '715', '716', '717', '718', '719', '720', '724', '725', '727', '731', '732', '734', '737', '740', '747', '754', '757', '760', '762', '763', '765', '770', '772', '773', '774', '775', '779', '781', '785', '786', '801', '802', '803', '804', '805', '806', '808', '810', '812', '813', '814', '815', '816', '817', '818', '820', '828', '830', '831', '832', '843', '845', '847', '848', '850', '856', '857', '858', '859', '860', '862', '863', '864', '865', '870', '872', '878', '901', '903', '904', '906', '907', '908', '909', '910', '912', '913', '914', '915', '916', '917', '918', '919', '920', '925', '928', '929', '930', '931', '934', '936', '937', '940', '941', '947', '949', '951', '952', '954', '956', '959', '970', '971', '972', '973', '978', '979', '980', '984', '985', '989']
                if clean_number[:3] in us_area_codes:
                    return f"+1{clean_number}"
        elif len(clean_number) == 12 and clean_number.startswith('57'):
            # 12 dígitos con código país 57: 573001234567 -> +573001234567
            return f"+{clean_number}"
        elif len(clean_number) == 13 and clean_number.startswith('573'):
            # 13 dígitos: +573001234567 ya formateado
            return f"+{clean_number}"
        elif len(clean_number) == 11:
            # 11 dígitos, verificar diferentes casos
            if clean_number.startswith('573'):
                # 573xxxxxxxx -> +573xxxxxxxx (formato incompleto)
                return f"+{clean_number}"
            elif clean_number.startswith('57'):
                # 57xxxxxxxxx -> +57xxxxxxxxx
                return f"+{clean_number}"

        # México (+52)
        elif len(clean_number) == 10 and clean_number.startswith(('55', '33', '81', '22')):
            # Números mexicanos comunes (CDMX, Guadalajara, Monterrey, Puebla)
            return f"+52{clean_number}"
        elif len(clean_number) == 12 and clean_number.startswith('52'):
            return f"+{clean_number}"

        # Reino Unido (+44)
        elif len(clean_number) == 10 and clean_number.startswith('7'):
            # Móviles UK
            return f"+44{clean_number}"
        elif len(clean_number) == 12 and clean_number.startswith('44'):
            return f"+{clean_number}"

        # Canadá (+1) - similar a US
        elif len(clean_number) == 10:
            # Verificar códigos de área canadienses comunes
            canadian_area_codes = ['204', '236', '249', '250', '289', '306', '343', '365', '403', '416', '418', '431', '437', '438', '450', '506', '514', '519', '548', '579', '581', '587', '604', '613', '647', '705', '709', '778', '780', '782', '807', '819', '825', '867', '873', '902', '905']
            if clean_number[:3] in canadian_area_codes:
                return f"+1{clean_number}"

        # Formato ya con código internacional (sin +)
        if len(clean_number) >= 11:
            # Verificar códigos de país comunes
            country_codes = {
                '1': [11],     # US/Canada: +1 + 10 digits
                '44': [12, 13], # UK: +44 + 10/11 digits
                '52': [12, 13], # Mexico: +52 + 10/11 digits
                '57': [12, 13], # Colombia: +57 + 10/11 digits
                '33': [11],     # France: +33 + 9 digits
                '49': [11, 12], # Germany: +49 + 10/11 digits
                '34': [11],     # Spain: +34 + 9 digits
            }

            for code, valid_lengths in country_codes.items():
                if clean_number.startswith(code) and len(clean_number) in valid_lengths:
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
    
    def _parse_twilio_error(self, error: TwilioException) -> str:
        """
        Parsea errores de Twilio a mensajes comprensibles.

        Args:
            error: Error de Twilio

        Returns:
            str: Mensaje de error comprensible
        """
        error_messages = {
            20003: "Error de autenticación Twilio",
            21211: "Número de teléfono inválido",
            21614: "Número no válido para SMS",
            21408: "Desde número no autorizado",
            30007: "Error de entrega del mensaje",
            30008: "Mensaje rechazado por operador"
        }

        if hasattr(error, 'code') and error.code in error_messages:
            return error_messages[error.code]

        return f"Error Twilio: {str(error)}"

    def send_notification_sms(
        self,
        phone_number: str,
        message: str,
        message_type: str = "notification"
    ) -> Tuple[bool, str]:
        """
        Envía SMS de notificación general.

        Args:
            phone_number: Número de teléfono destino
            message: Mensaje a enviar
            message_type: Tipo de mensaje para logging

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            if not self.sms_enabled:
                return False, "Servicio SMS deshabilitado"

            formatted_number = self._format_international_phone(phone_number)
            if not formatted_number:
                return False, "Número telefónico inválido"

            # Check rate limit
            rate_allowed, rate_message = self._check_rate_limit(formatted_number)
            if not rate_allowed:
                return False, rate_message

            if self.simulation_mode:
                logger.info(f"SIMULACIÓN SMS {message_type} - Para: {formatted_number}")
                print(f"📱 SIMULACIÓN SMS {message_type.upper()}:")
                print(f"   Para: {formatted_number}")
                print(f"   Mensaje: {message}")
                print(f"   Timestamp: {datetime.now()}")

                self._increment_rate_limit(formatted_number)
                return True, f"SMS {message_type} simulado enviado"

            # Send real SMS
            sms_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=formatted_number
            )

            self._increment_rate_limit(formatted_number)
            logger.info(f"SMS {message_type} enviado. SID: {sms_message.sid}")
            return True, f"SMS {message_type} enviado exitosamente"

        except TwilioException as e:
            error_details = self._parse_twilio_error(e)
            logger.error(f"Error Twilio enviando SMS {message_type}: {error_details}")
            return False, f"Error enviando SMS: {error_details}"
        except Exception as e:
            logger.error(f"Error enviando SMS {message_type}: {str(e)}")
            return False, f"Error interno: {str(e)}"

    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Valida si un número telefónico tiene formato correcto.

        Args:
            phone_number: Número a validar

        Returns:
            bool: True si es válido
        """
        return self._format_international_phone(phone_number) is not None

    def get_service_status(self) -> Dict[str, any]:
        """
        Obtiene el estado del servicio SMS.

        Returns:
            Dict: Estado del servicio
        """
        status = {
            "service_enabled": self.sms_enabled,
            "simulation_mode": self.simulation_mode,
            "twilio_configured": bool(self.account_sid and self.auth_token and self.from_number),
            "rate_limiting_enabled": self.redis_service is not None,
            "rate_limit_per_number": self.rate_limit_per_number,
            "rate_limit_window_seconds": self.rate_limit_window
        }

        if not self.simulation_mode and hasattr(self, 'client'):
            try:
                # Test connection
                account = self.client.api.accounts(self.account_sid).fetch()
                status["twilio_connection"] = "active"
                status["twilio_account_status"] = account.status
            except:
                status["twilio_connection"] = "failed"
                status["twilio_account_status"] = "unknown"
        else:
            status["twilio_connection"] = "simulation"

        return status

    def get_rate_limit_status(self, phone_number: str) -> Dict[str, any]:
        """
        Obtiene el estado de rate limiting para un número.

        Args:
            phone_number: Número de teléfono

        Returns:
            Dict: Estado de rate limiting
        """
        if not self.redis_service:
            return {"rate_limiting": "disabled"}

        try:
            rate_limit_key = f"sms_rate_limit:{phone_number}"
            current_count = self.redis_service.get(rate_limit_key)

            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)

            remaining = max(0, self.rate_limit_per_number - current_count)

            return {
                "phone_number": phone_number,
                "current_count": current_count,
                "limit": self.rate_limit_per_number,
                "remaining": remaining,
                "window_seconds": self.rate_limit_window,
                "blocked": current_count >= self.rate_limit_per_number
            }
        except Exception as e:
            logger.error(f"Error obteniendo rate limit status: {str(e)}")
            return {"error": str(e)}
