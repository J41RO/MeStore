from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.sms_service import SMSService
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
