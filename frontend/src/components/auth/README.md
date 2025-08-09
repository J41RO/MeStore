# 🔐 Componente OTP Verification

## 📋 Descripción

Componente React completo para verificación OTP por Email y SMS, integrado con el backend FastAPI de MeStore.

## 🚀 Características

- ✅ Verificación por Email y SMS
- ✅ Input de 6 dígitos con auto-focus
- ✅ Cooldown de 60 segundos para reenvío
- ✅ Manejo completo de errores
- ✅ Estados de loading y feedback visual
- ✅ Diseño responsive y accesible
- ✅ TypeScript completo

## 📡 Endpoints Backend Integrados

- `POST /api/v1/auth/send-verification-email` - Solicitar OTP por email
- `POST /api/v1/auth/send-verification-sms` - Solicitar OTP por SMS
- `POST /api/v1/auth/verify-email-otp` - Verificar código email
- `POST /api/v1/auth/verify-phone-otp` - Verificar código SMS

## 🎮 Uso del Componente

```tsx
import OTPVerification from './auth/OTPVerification';

function MyComponent() {
  const handleSuccess = (type: 'EMAIL' | 'SMS') => {
    console.log(`Verificación ${type} exitosa`);
  };

  return (
    <OTPVerification
      onVerificationSuccess={handleSuccess}
      onClose={() => setShowOTP(false)}
    />
  );
}
```

## 🎨 Estilos

Los estilos están en `OTPVerification.css` y son completamente personalizables.

## 🧪 Testing

Para probar el componente, usar `OTPDemo.tsx` que incluye:

- Modal overlay
- Estados de éxito/error
- Ejemplos de uso

## 🔧 Configuración Backend Requerida

Variables de entorno necesarias en el backend:

```
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_FROM_NUMBER=+573XXXXXXXX
OTP_EXPIRATION_MINUTES=5
OTP_MAX_ATTEMPTS=3
```

## ⚡ Estado Actual

- ✅ Componente completamente funcional
- ✅ Integrado con backend MeStore
- ✅ Build de producción exitoso
- ✅ Demo disponible en App.tsx
