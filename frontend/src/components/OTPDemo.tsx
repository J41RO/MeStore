import React, { useState } from 'react';
import OTPVerification from './auth/OTPVerification';

const OTPDemo: React.FC = () => {
  const [showOTP, setShowOTP] = useState(false);
  const [verificationResult, setVerificationResult] = useState<string>('');

  const handleVerificationSuccess = (type: 'EMAIL' | 'SMS') => {
    setVerificationResult(`✅ Verificación ${type} exitosa!`);
    setShowOTP(false);
  };

  const handleClose = () => {
    setShowOTP(false);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>🔐 Demo Verificación OTP</h1>
      <p>Componente de verificación OTP por Email/SMS</p>
      
      {!showOTP && (
        <div>
          <button
            onClick={() => setShowOTP(true)}
            style={{
              padding: '12px 24px',
              background: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            🚀 Abrir Verificación OTP
          </button>
        </div>
      )}

      {showOTP && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <OTPVerification
            onVerificationSuccess={handleVerificationSuccess}
            onClose={handleClose}
          />
        </div>
      )}

      {verificationResult && (
        <div style={{
          marginTop: '20px',
          padding: '15px',
          background: '#d4edda',
          border: '1px solid #c3e6cb',
          borderRadius: '4px',
          color: '#155724'
        }}>
          {verificationResult}
        </div>
      )}

      <div style={{ marginTop: '30px' }}>
        <h3>📋 Funcionalidades implementadas:</h3>
        <ul>
          <li>✅ Selección entre verificación por Email y SMS</li>
          <li>✅ Envío de código OTP a backend</li>
          <li>✅ Input de 6 dígitos con auto-focus</li>
          <li>✅ Cooldown de 60 segundos para reenvío</li>
          <li>✅ Validación y verificación de código</li>
          <li>✅ Manejo de errores y estados de loading</li>
          <li>✅ Diseño responsive y accesible</li>
        </ul>
      </div>
    </div>
  );
};

export default OTPDemo;
