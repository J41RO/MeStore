from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.sms_service import SMSService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class SMSTest(BaseModel):
    phone: str
    message: str = 'Test SMS from MeStocker - Your verification code is: 123456'


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
            'sms_enabled': sms_service.sms_enabled
        }
    except Exception as e:
        logger.error(f'❌ Error checking SMS service: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))
