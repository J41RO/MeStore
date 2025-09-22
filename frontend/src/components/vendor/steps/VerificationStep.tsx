import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Button } from '../../ui/Button';

interface VerificationStepProps {
  email: string;
  phone: string;
  onNext: () => void;
  onPrev: () => void;
  isLoading: boolean;
}

export const VerificationStep: React.FC<VerificationStepProps> = ({
  email,
  phone,
  onNext,
  onPrev,
  isLoading
}) => {
  const [otpValues, setOtpValues] = useState<string[]>(['', '', '', '', '', '']);
  const [isVerifying, setIsVerifying] = useState(false);
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes
  const [canResend, setCanResend] = useState(false);
  const [verificationMethod, setVerificationMethod] = useState<'sms' | 'email'>('sms');

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Countdown timer
  useEffect(() => {
    if (timeLeft > 0 && !canResend) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0) {
      setCanResend(true);
    }
  }, [timeLeft, canResend]);

  // Format time display
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Handle OTP input change
  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) {
      // Handle paste
      const pastedCode = value.slice(0, 6);
      const newOtpValues = [...otpValues];
      for (let i = 0; i < pastedCode.length && i < 6; i++) {
        newOtpValues[i] = pastedCode[i];
      }
      setOtpValues(newOtpValues);

      // Focus last filled input or next empty
      const nextIndex = Math.min(pastedCode.length, 5);
      inputRefs.current[nextIndex]?.focus();
    } else {
      // Single character input
      const newOtpValues = [...otpValues];
      newOtpValues[index] = value;
      setOtpValues(newOtpValues);

      // Auto-focus next input
      if (value && index < 5) {
        inputRefs.current[index + 1]?.focus();
      }
    }
  };

  // Handle backspace
  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !otpValues[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  // Verify OTP
  const handleVerifyOtp = async () => {
    const otp = otpValues.join('');
    if (otp.length !== 6) {
      return;
    }

    setIsVerifying(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      // For demo purposes, accept any 6-digit code
      if (otp.length === 6) {
        onNext();
      } else {
        alert('Código inválido. Intenta nuevamente.');
        setOtpValues(['', '', '', '', '', '']);
        inputRefs.current[0]?.focus();
      }
    } catch (error) {
      console.error('Verification failed:', error);
      alert('Error en la verificación. Intenta nuevamente.');
    } finally {
      setIsVerifying(false);
    }
  };

  // Resend code
  const handleResendCode = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      setTimeLeft(300); // Reset timer
      setCanResend(false);
      setOtpValues(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();

      alert(`Nuevo código enviado por ${verificationMethod === 'sms' ? 'SMS' : 'email'}`);
    } catch (error) {
      console.error('Resend failed:', error);
      alert('Error enviando código. Intenta nuevamente.');
    }
  };

  // Switch verification method
  const switchMethod = (method: 'sms' | 'email') => {
    setVerificationMethod(method);
    setOtpValues(['', '', '', '', '', '']);
    setTimeLeft(300);
    setCanResend(false);
    inputRefs.current[0]?.focus();
  };

  const isOtpComplete = otpValues.every(value => value !== '') && otpValues.join('').length === 6;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Step Header */}
      <div className="text-center mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Verificación de Contacto
        </h3>
        <p className="text-gray-600 text-sm">
          Confirma tu identidad con el código que enviamos
        </p>
      </div>

      {/* Verification Method Selector */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-center space-x-4">
          <button
            onClick={() => switchMethod('sms')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              verificationMethod === 'sms'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            <span className="text-xl">📱</span>
            <span className="font-medium">SMS</span>
          </button>
          <button
            onClick={() => switchMethod('email')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              verificationMethod === 'email'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            <span className="text-xl">📧</span>
            <span className="font-medium">Email</span>
          </button>
        </div>
      </div>

      {/* Verification Info */}
      <div className="text-center">
        <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
          <span className="text-2xl">
            {verificationMethod === 'sms' ? '📱' : '📧'}
          </span>
        </div>
        <p className="text-gray-600 mb-4">
          Enviamos un código de 6 dígitos{' '}
          {verificationMethod === 'sms' ? 'por SMS' : 'por email'} a:
        </p>
        <p className="font-semibold text-gray-900 mb-6">
          {verificationMethod === 'sms'
            ? `+57 ${phone?.replace(/(\d{3})(\d{3})(\d{4})/, '$1 $2 $3') || 'XXX XXX XXXX'}`
            : email || 'tu@email.com'
          }
        </p>
      </div>

      {/* OTP Input Fields */}
      <div className="flex justify-center space-x-3 mb-6">
        {otpValues.map((value, index) => (
          <input
            key={index}
            ref={(el) => (inputRefs.current[index] = el)}
            type="text"
            inputMode="numeric"
            maxLength={6}
            value={value}
            onChange={(e) => handleOtpChange(index, e.target.value.replace(/\D/g, ''))}
            onKeyDown={(e) => handleKeyDown(index, e)}
            className="w-12 h-12 text-center text-xl font-bold border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
            placeholder="0"
            data-testid={`otp-input-${index}`}
            disabled={isVerifying}
          />
        ))}
      </div>

      {/* Timer and Resend */}
      <div className="text-center space-y-3">
        {!canResend ? (
          <p className="text-sm text-gray-500">
            El código expira en{' '}
            <span className="font-medium text-gray-700">{formatTime(timeLeft)}</span>
          </p>
        ) : (
          <p className="text-sm text-red-600">
            El código ha expirado
          </p>
        )}

        <div className="flex justify-center">
          {canResend ? (
            <button
              onClick={handleResendCode}
              className="text-blue-600 hover:text-blue-800 font-medium text-sm"
            >
              Enviar nuevo código
            </button>
          ) : (
            <button
              onClick={handleResendCode}
              className="text-gray-400 text-sm cursor-not-allowed"
              disabled
            >
              Reenviar código
            </button>
          )}
        </div>
      </div>

      {/* Verify Button */}
      <div className="text-center">
        <Button
          onClick={handleVerifyOtp}
          disabled={!isOtpComplete || isVerifying}
          className="w-full max-w-xs"
          data-testid="verify-otp"
        >
          {isVerifying ? (
            <div className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Verificando...
            </div>
          ) : (
            'Verificar Código'
          )}
        </Button>
      </div>

      {/* Help Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1">
            <h4 className="text-sm font-medium text-blue-900 mb-1">
              ¿No recibiste el código?
            </h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Revisa tu bandeja de spam (si es por email)</li>
              <li>• Verifica que el número/email sea correcto</li>
              <li>• Espera unos minutos, a veces hay retraso</li>
              <li>• Prueba cambiar el método de verificación</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="flex space-x-4 pt-4">
        <Button
          type="button"
          variant="outline"
          onClick={onPrev}
          className="flex-1"
          disabled={isLoading || isVerifying}
        >
          Atrás
        </Button>
        <Button
          onClick={() => {
            // Skip verification for demo
            onNext();
          }}
          variant="outline"
          className="flex-1"
          disabled={isLoading || isVerifying}
        >
          Verificar después
        </Button>
      </div>
    </motion.div>
  );
};