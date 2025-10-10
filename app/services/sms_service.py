# ~/app/services/sms_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio SMS con Twilio
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Servicio SMS para MeStore con integración completa de Twilio.

Este módulo maneja el envío de SMS:
- SMS de verificación con códigos OTP
- Configuración completa Twilio API
- Formateo de números telefónicos colombianos
- Rate limiting y control de frecuencia
- Manejo avanzado de errores
- Fallback a modo simulación en desarrollo
"""

import os
import time
from typing import Optional, Dict, Tuple
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

        # Check configuration
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning(
                "Twilio credentials no configuradas. SMS service en modo simulación.\n"
                "Configurar: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER"
            )
            self.simulation_mode = True
            self.client = None
        else:
            self.simulation_mode = False
            # Initialize Twilio client
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("SMS Service inicializado correctamente con Twilio")
            except Exception as e:
                logger.error(f"Error inicializando Twilio client: {str(e)}")
                self.simulation_mode = True
                self.client = None

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

    def _send_twilio_sms(self, phone_number: str, message: str) -> dict:
        """
        Envía SMS usando Twilio API.

        Args:
            phone_number: Número de teléfono en formato internacional (+57...)
            message: Mensaje a enviar

        Returns:
            dict: Respuesta de Twilio API

        Raises:
            Exception: Si hay error en el envío
        """
        try:
            from twilio.base.exceptions import TwilioException

            message_response = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone_number
            )

            result = {
                'sid': message_response.sid,
                'status': message_response.status,
                'to': message_response.to,
                'from': message_response.from_,
                'date_created': str(message_response.date_created)
            }

            logger.info(f"✅ Twilio API response - SID: {message_response.sid}, Status: {message_response.status}")
            return result

        except TwilioException as e:
            logger.error(f"❌ Twilio API error: {str(e)}")
            raise Exception(f"Twilio API error: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Error enviando SMS con Twilio: {str(e)}")
            raise

    async def send_otp_sms(
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

            # Crear mensaje SMS usando formato especificado
            message_body = f"Tu código de verificación MeStocker es: {otp_code}"

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

            # Enviar SMS real con Twilio API
            try:
                result = self._send_twilio_sms(formatted_number, message_body)

                # Increment rate limit only on successful send
                self._increment_rate_limit(formatted_number)

                logger.info(f"SMS OTP enviado exitosamente a {formatted_number}")
                return True, f"SMS enviado a {formatted_number}"

            except Exception as e:
                logger.error(f"Error enviando SMS OTP con Twilio: {str(e)}")
                return False, f"Error enviando SMS: {str(e)}"

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

        # Colombia (+57) - prioridad para MeStocker Colombia
        if len(clean_number) == 10:
            # 10 dígitos: puede ser celular (300..., 301..., etc.)
            if clean_number.startswith('3'):
                # Celular: 3001234567 -> +573001234567
                return f"+57{clean_number}"
        elif len(clean_number) == 12 and clean_number.startswith('57'):
            # 12 dígitos con código país 57: 573001234567 -> +573001234567
            return f"+{clean_number}"

        # Formato no reconocido
        logger.warning(f"Formato de teléfono no reconocido: {phone_number}")
        return None

    async def send_sms(self, to_phone: str, message: str) -> dict:
        """
        Envía SMS genérico usando Twilio API.
        Método wrapper para compatibilidad con test endpoint.

        Args:
            to_phone: Número de teléfono destino en formato internacional
            message: Mensaje a enviar

        Returns:
            dict: Detalles del SMS enviado

        Raises:
            Exception: Si hay error enviando el SMS
        """
        try:
            # Formatear número telefónico
            formatted_number = self._format_international_phone(to_phone)
            if not formatted_number:
                raise ValueError(f"Número telefónico inválido: {to_phone}")

            # Verificar rate limiting
            rate_allowed, rate_message = self._check_rate_limit(formatted_number)
            if not rate_allowed:
                raise Exception(f"Rate limit excedido: {rate_message}")

            if self.simulation_mode:
                logger.info(f"🧪 SIMULACIÓN SMS - Para: {formatted_number}")
                print(f"📱 SIMULACIÓN SMS:")
                print(f"   Para: {formatted_number}")
                print(f"   Mensaje: {message}")
                print(f"   Timestamp: {datetime.now()}")

                self._increment_rate_limit(formatted_number)
                return {
                    'id': f'SIMULATED_{int(time.time())}',
                    'status': 'simulated',
                    'to': formatted_number,
                    'date_sent': str(datetime.now())
                }

            # Enviar SMS real con Twilio API
            result = self._send_twilio_sms(formatted_number, message)

            # Increment rate limit
            self._increment_rate_limit(formatted_number)

            logger.info(f"✅ SMS enviado exitosamente con Twilio API")

            return {
                'id': result.get('sid', 'unknown'),
                'status': result.get('status', 'sent'),
                'to': formatted_number,
                'date_sent': result.get('date_created', str(datetime.now()))
            }

        except Exception as e:
            logger.error(f"❌ Error enviando SMS: {str(e)}")
            raise

    async def send_notification_sms(
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
            try:
                result = self._send_twilio_sms(formatted_number, message)

                self._increment_rate_limit(formatted_number)
                logger.info(f"SMS {message_type} enviado con Twilio API")
                return True, f"SMS {message_type} enviado exitosamente"

            except Exception as e:
                logger.error(f"Error enviando SMS {message_type} con Twilio: {str(e)}")
                return False, f"Error enviando SMS: {str(e)}"

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
            "rate_limit_window_seconds": self.rate_limit_window,
            "provider": "Twilio"
        }

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

    async def send_verification_code(self, phone_number: str, channel: str = "sms") -> dict:
        """
        Envía código de verificación usando Twilio Verify API (si está configurado).

        Args:
            phone_number: Número de teléfono en formato internacional (+57XXXXXXXXXX)
            channel: Canal de envío ('sms'). Default: 'sms'

        Returns:
            dict: Información de la verificación enviada

        Raises:
            ValueError: Si el número de teléfono es inválido
            Exception: Si hay error al enviar la verificación
        """
        try:
            # Formatear número telefónico
            formatted_number = self._format_international_phone(phone_number)
            if not formatted_number:
                logger.error(f"❌ Número telefónico inválido: {phone_number}")
                raise ValueError(f"Número telefónico inválido: {phone_number}")

            logger.info(f"📱 Sending verification code to {formatted_number} via {channel}")

            if self.simulation_mode or not self.verify_service_sid:
                # Generar código de verificación (6 dígitos) para simulación
                import random
                verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

                logger.info(f"🧪 SIMULACIÓN - Código de verificación: {verification_code}")
                return {
                    'success': True,
                    'status': 'simulated',
                    'to': formatted_number,
                    'channel': channel,
                    'code': verification_code,
                    'provider': 'Twilio (Simulation)'
                }

            # Usar Twilio Verify API si está configurado
            verification = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verifications \
                .create(to=formatted_number, channel=channel)

            logger.info(f"✅ Verification sent successfully to {formatted_number}")

            return {
                'success': True,
                'status': verification.status,
                'to': verification.to,
                'channel': verification.channel,
                'provider': 'Twilio Verify'
            }

        except Exception as e:
            logger.error(f"❌ Error sending verification code: {str(e)}")
            raise

    async def verify_code(self, phone_number: str, code: str) -> dict:
        """
        Verifica el código de verificación ingresado por el usuario usando Twilio Verify API.

        Args:
            phone_number: Número de teléfono en formato internacional
            code: Código de verificación de 6 dígitos ingresado por el usuario

        Returns:
            dict: Resultado de la verificación

        Raises:
            ValueError: Si el número de teléfono es inválido
            NotImplementedError: Si Twilio Verify no está configurado
        """
        try:
            formatted_number = self._format_international_phone(phone_number)
            if not formatted_number:
                raise ValueError(f"Número telefónico inválido: {phone_number}")

            if self.simulation_mode or not self.verify_service_sid:
                logger.warning("Twilio Verify no configurado - usar OTPService con base de datos")
                raise NotImplementedError(
                    "La verificación del código debe implementarse usando OTPService "
                    "y comparar contra códigos almacenados en la base de datos"
                )

            # Usar Twilio Verify API
            verification_check = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verification_checks \
                .create(to=formatted_number, code=code)

            return {
                'success': verification_check.status == 'approved',
                'status': verification_check.status,
                'to': verification_check.to,
                'provider': 'Twilio Verify'
            }

        except Exception as e:
            logger.error(f"❌ Error verifying code: {str(e)}")
            raise
