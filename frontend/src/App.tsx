import { useState } from 'react'
import './App.css'
import OTPDemo from './components/OTPDemo'
import ForgotPassword from './components/auth/ForgotPassword'
import ResetPassword from './components/auth/ResetPassword'
import './components/auth/PasswordReset.css'

type DemoView = 'otp' | 'forgot' | 'reset' | 'home'

function App() {
  const [currentView, setCurrentView] = useState<DemoView>('home')

  const renderView = () => {
    switch (currentView) {
      case 'otp':
        return <OTPDemo />
      case 'forgot':
        return <ForgotPassword onBackToLogin={() => setCurrentView('home')} />
      case 'reset':
        return <ResetPassword />
      default:
        return (
          <div style={{ padding: '40px', textAlign: 'center', maxWidth: '800px', margin: '0 auto' }}>
            <h1>🔐 MeStore Auth Components Demo</h1>
            <p>Demostración de componentes de autenticación implementados</p>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '20px',
              marginTop: '40px'
            }}>
              <div style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '20px',
                background: '#f8f9fa'
              }}>
                <h3>📱 Verificación OTP</h3>
                <p>Componente completo para verificación por Email/SMS con códigos OTP</p>
                <button 
                  onClick={() => setCurrentView('otp')}
                  style={{
                    padding: '10px 20px',
                    background: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Ver Demo OTP
                </button>
              </div>

              <div style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '20px',
                background: '#f8f9fa'
              }}>
                <h3>📧 Recuperar Contraseña</h3>
                <p>Componente para solicitar recuperación de contraseña por email</p>
                <button 
                  onClick={() => setCurrentView('forgot')}
                  style={{
                    padding: '10px 20px',
                    background: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Ver Demo Forgot Password
                </button>
              </div>

              <div style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '20px',
                background: '#f8f9fa'
              }}>
                <h3>🔑 Reset Contraseña</h3>
                <p>Componente para restablecer contraseña con token de validación</p>
                <button 
                  onClick={() => setCurrentView('reset')}
                  style={{
                    padding: '10px 20px',
                    background: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Ver Demo Reset Password
                </button>
              </div>
            </div>

            <div style={{ 
              marginTop: '40px', 
              padding: '20px', 
              background: '#e8f5e8', 
              borderRadius: '8px',
              border: '1px solid #28a745'
            }}>
              <h3>✅ Estado del Proyecto</h3>
              <ul style={{ textAlign: 'left', maxWidth: '500px', margin: '0 auto' }}>
                <li>✅ <strong>Backend OTP:</strong> Completamente funcional</li>
                <li>✅ <strong>Frontend OTP:</strong> Componente React/TypeScript</li>
                <li>✅ <strong>Password Reset:</strong> Componentes implementados</li>
                <li>✅ <strong>TypeScript:</strong> Configuración limpia</li>
                <li>✅ <strong>Build Pipeline:</strong> Funcionando perfectamente</li>
              </ul>
            </div>
          </div>
        )
    }
  }

  return (
    <div className="App">
      {currentView !== 'home' && (
        <button 
          onClick={() => setCurrentView('home')}
          style={{
            position: 'fixed',
            top: '20px',
            left: '20px',
            padding: '8px 16px',
            background: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            zIndex: 1000
          }}
        >
          ← Volver al Demo
        </button>
      )}
      {renderView()}
    </div>
  )
}

export default App
