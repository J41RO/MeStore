from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.sms_service import SMSService
from app.core.database import get_db
from app.models.user import User
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class SMSTest(BaseModel):
    phone: str
    message: str = 'Test SMS from MeStocker - Your verification code is: 123456'


class VerificationRequest(BaseModel):
    phone: str
    channel: str = 'sms'  # 'sms' or 'call'


class VerificationCheck(BaseModel):
    phone: str
    code: str


@router.post('/send-sms', tags=['Test'])
async def test_send_sms(data: SMSTest):
    """
    Endpoint temporal para probar envío de SMS con Twilio

    Números de prueba:
    - US: +17379771943
    - Colombia: +573150518480
    """
    try:
        logger.info(f'🧪 Testing SMS to {data.phone}')

        sms_service = SMSService()
        result = await sms_service.send_sms(
            to_phone=data.phone,
            message=data.message
        )

        logger.info(f'✅ SMS sent successfully: {result}')
        return {
            'success': True,
            'message': 'SMS sent successfully',
            'details': result,
            'phone': data.phone
        }
    except Exception as e:
        logger.error(f'❌ Error sending SMS: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/sms-status', tags=['Test'])
async def check_sms_service():
    """Verifica el estado del servicio SMS"""
    try:
        sms_service = SMSService()

        # Verificar que Twilio esté configurado
        if not sms_service.from_number:
            return {
                'success': False,
                'message': 'Twilio phone number not configured',
                'simulation_mode': sms_service.simulation_mode
            }

        return {
            'success': True,
            'message': 'SMS service is ready',
            'from_phone': sms_service.from_number,
            'provider': 'Twilio',
            'simulation_mode': sms_service.simulation_mode,
            'sms_enabled': sms_service.sms_enabled,
            'verify_service_configured': bool(sms_service.verify_service_sid)
        }
    except Exception as e:
        logger.error(f'❌ Error checking SMS service: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/send-verification-code', tags=['Test'])
async def send_verification_code(data: VerificationRequest):
    """
    Envía código de verificación usando Twilio Verify

    Este endpoint usa Twilio Verify Service (NO SMS directo) para cumplir
    con regulaciones A2P 10DLC en Estados Unidos.

    Test numbers:
    - US: +17379771943
    - Colombia: +573150518480

    Returns:
        - success: True si se envió correctamente
        - status: 'pending' si está pendiente de verificación
        - to: Número al que se envió
        - channel: Canal usado ('sms' o 'call')
    """
    try:
        logger.info(f'📱 Sending verification code to {data.phone} via {data.channel}')

        sms_service = SMSService()
        result = await sms_service.send_verification_code(
            phone_number=data.phone,
            channel=data.channel
        )

        logger.info(f'✅ Verification code sent: {result}')
        return result

    except ValueError as e:
        logger.error(f'❌ Invalid phone number: {str(e)}')
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f'❌ Error sending verification code: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/verify-code', tags=['Test'])
async def verify_code(data: VerificationCheck):
    """
    Verifica el código de verificación ingresado por el usuario

    Args:
        phone: Número de teléfono en formato internacional
        code: Código de 6 dígitos recibido por SMS

    Returns:
        - success: True si el código es válido
        - status: 'approved' si es válido, otro estado si no
        - valid: True si el código es correcto
        - message: Mensaje descriptivo del resultado
    """
    try:
        logger.info(f'🔍 Verifying code for {data.phone}')

        sms_service = SMSService()
        result = await sms_service.verify_code(
            phone_number=data.phone,
            code=data.code
        )

        if result['valid']:
            logger.info(f'✅ Code verified successfully for {data.phone}')
        else:
            logger.warning(f'⚠️ Code verification failed for {data.phone}: {result.get("status")}')

        return result

    except ValueError as e:
        logger.error(f'❌ Invalid input: {str(e)}')
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f'❌ Error verifying code: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/debug/otp-status', tags=['Test', 'Debug'])
async def debug_otp_status(
    phone: str,
    db: AsyncSession = Depends(get_db)
):
    """
    🔍 ENDPOINT DE DIAGNÓSTICO - Ver estado del OTP de un usuario
    
    Uso: GET /api/v1/test/debug/otp-status?phone=+17379771943
    
    Returns información completa del estado de verificación OTP.
    """
    try:
        logger.info(f'🔍 Diagnosticando OTP para {phone}')
        
        # Buscar usuario por teléfono
        result = await db.execute(
            select(User).where(User.telefono == phone)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {
                'success': False,
                'message': f'No se encontró usuario con teléfono {phone}',
                'phone_searched': phone,
                'suggestion': 'Verifica que el número esté en formato E.164 (+1234567890)'
            }
        
        # Calcular tiempo restante si hay código activo
        time_remaining = None
        is_expired = False
        
        if user.otp_expires_at:
            now = datetime.utcnow()
            expires = user.otp_expires_at.replace(tzinfo=None)
            
            if now < expires:
                remaining = expires - now
                time_remaining = {
                    'minutes': remaining.seconds // 60,
                    'seconds': remaining.seconds % 60,
                    'total_seconds': remaining.seconds
                }
            else:
                is_expired = True
                expired_ago = now - expires
                time_remaining = {
                    'expired_ago_minutes': expired_ago.seconds // 60,
                    'expired_ago_seconds': expired_ago.seconds % 60
                }
        
        # Construir respuesta de diagnóstico
        return {
            'success': True,
            'message': 'Información de OTP encontrada',
            'user_info': {
                'nombre': user.nombre,
                'apellido': user.apellido,
                'email': user.email,
                'telefono': user.telefono,
                'user_type': user.user_type
            },
            'otp_status': {
                'code_in_database': user.otp_secret,
                'code_type': user.otp_type,
                'expires_at': user.otp_expires_at.isoformat() if user.otp_expires_at else None,
                'is_expired': is_expired,
                'time_remaining': time_remaining,
                'failed_attempts': user.otp_attempts,
                'max_attempts': 5,
                'is_blocked': user.otp_attempts >= 5,
                'last_sent_at': user.last_otp_sent.isoformat() if user.last_otp_sent else None
            },
            'verification_status': {
                'email_verified': user.email_verified,
                'phone_verified': user.phone_verified,
                'account_status': user.account_status,
                'is_active': user.is_active
            },
            'diagnosis': {
                'can_verify': user.otp_secret is not None and not is_expired and user.otp_attempts < 5,
                'issues': []
            }
        }
        
    except Exception as e:
        logger.error(f'❌ Error en diagnóstico OTP: {str(e)}', exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f'Error en diagnóstico: {str(e)}'
        )
