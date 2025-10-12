import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Clock, Mail, CheckCircle, ArrowRight, Home } from 'lucide-react';

interface LocationState {
  message?: string;
  email?: string;
}

const RegistrationPending: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState;

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-orange-50 to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-2xl overflow-hidden">
        {/* Header with gradient */}
        <div className="bg-gradient-to-r from-orange-500 to-purple-600 p-8 text-white">
          <div className="flex items-center justify-center mb-4">
            <Clock className="w-16 h-16" />
          </div>
          <h1 className="text-3xl font-bold text-center mb-2">
            Registro en Revisión
          </h1>
          <p className="text-center text-orange-100">
            Tu cuenta de vendedor está siendo revisada por nuestro equipo
          </p>
        </div>

        {/* Content */}
        <div className="p-8">
          {/* Message */}
          {state?.message && (
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-yellow-800 text-center">
                {state.message}
              </p>
            </div>
          )}

          {/* Email notification */}
          {state?.email && (
            <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-start space-x-3">
              <Mail className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-blue-900 font-medium mb-1">
                  Confirmación enviada
                </p>
                <p className="text-sm text-blue-700">
                  Hemos enviado un email de confirmación a: <strong>{state.email}</strong>
                </p>
              </div>
            </div>
          )}

          {/* Next Steps */}
          <div className="space-y-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
              <CheckCircle className="w-6 h-6 text-green-600" />
              <span>Próximos Pasos</span>
            </h2>

            <div className="space-y-4">
              <div className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-bold">
                  1
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Revisión de Documentos
                  </h3>
                  <p className="text-sm text-gray-600">
                    Nuestro equipo está verificando la información y documentos que proporcionaste.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-bold">
                  2
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Verificación de Identidad
                  </h3>
                  <p className="text-sm text-gray-600">
                    Validaremos tu identidad y la información fiscal proporcionada.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-bold">
                  3
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Notificación por Email
                  </h3>
                  <p className="text-sm text-gray-600">
                    Te notificaremos por email cuando tu cuenta sea aprobada y puedas comenzar a vender.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg mb-8">
            <h3 className="font-semibold text-blue-900 mb-2 flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span>Tiempo Estimado</span>
            </h3>
            <p className="text-sm text-blue-700">
              El proceso de revisión suele tomar <strong>menos de 72 horas hábiles</strong>.
              Te contactaremos si necesitamos información adicional.
            </p>
          </div>

          {/* Contact Info */}
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg mb-8">
            <h3 className="font-semibold text-purple-900 mb-2">
              ¿Necesitas ayuda?
            </h3>
            <p className="text-sm text-purple-700 mb-3">
              Si tienes preguntas sobre tu registro, contáctanos:
            </p>
            <div className="space-y-2 text-sm">
              <p className="text-purple-800">
                <strong>Email:</strong> soporte@mestocker.com
              </p>
              <p className="text-purple-800">
                <strong>WhatsApp:</strong> +57 300 123 4567
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-3">
            <button
              onClick={() => navigate('/')}
              className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-blue-700 shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center space-x-2"
            >
              <Home className="w-5 h-5" />
              <span>Volver al Inicio</span>
            </button>

            <button
              onClick={() => navigate('/login')}
              className="w-full py-3 px-4 border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-purple-600 hover:text-purple-600 transition-all duration-200 flex items-center justify-center space-x-2"
            >
              <ArrowRight className="w-5 h-5" />
              <span>Ir a Inicio de Sesión</span>
            </button>
          </div>

          {/* Note */}
          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              Una vez aprobada tu cuenta, podrás acceder con tu email y contraseña
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegistrationPending;
