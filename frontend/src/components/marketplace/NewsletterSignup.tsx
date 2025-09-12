import React, { useState } from 'react';
import { Mail, Check } from 'lucide-react';

const NewsletterSignup: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsLoading(true);
    
    // Simular llamada a API
    setTimeout(() => {
      setIsSubscribed(true);
      setIsLoading(false);
      setEmail('');
    }, 1000);
  };

  if (isSubscribed) {
    return (
      <section className="py-16 bg-blue-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-white rounded-lg p-8 shadow-xl">
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <Check className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              ¡Gracias por suscribirte!
            </h3>
            <p className="text-gray-600">
              Te enviaremos las mejores ofertas y productos destacados cada semana.
            </p>
            <button
              onClick={() => setIsSubscribed(false)}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              Suscribir otro email
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 bg-blue-600">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="text-white">
          <h2 className="text-3xl font-bold mb-4">
            Nunca te pierdas las mejores ofertas
          </h2>
          <p className="text-xl mb-8 text-blue-100">
            Suscríbete a nuestro newsletter y recibe ofertas exclusivas, 
            nuevos productos y tendencias del marketplace local.
          </p>

          <form onSubmit={handleSubmit} className="max-w-md mx-auto">
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="email"
                  placeholder="tu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:border-transparent text-gray-900"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="bg-yellow-500 hover:bg-yellow-600 text-blue-900 font-medium px-6 py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Suscribiendo...' : 'Suscribirse'}
              </button>
            </div>
          </form>

          <p className="text-sm text-blue-200 mt-4">
            No spam. Solo las mejores ofertas. Puedes cancelar en cualquier momento.
          </p>
        </div>
      </div>
    </section>
  );
};

export default NewsletterSignup;