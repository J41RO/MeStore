// ~/MeStore/frontend/src/components/SoporteModal.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - SoporteModal Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: SoporteModal.tsx
// Ruta: ~/MeStore/frontend/src/components/SoporteModal.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-14
// Última Actualización: 2025-08-14
// Versión: 1.0.0
// Propósito: Modal para contactar soporte técnico
//
// Modificaciones:
// 2025-08-14 - Creación inicial del modal
//
// ---------------------------------------------------------------------------------------------

import React, { useState } from 'react';
import { X, HelpCircle, Mail, Phone, MessageCircle } from 'lucide-react';

interface SoporteModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SoporteModal: React.FC<SoporteModalProps> = ({ isOpen, onClose }) => {
  const [selectedOption, setSelectedOption] = useState<string>('');
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implementar lógica de envío de soporte
    console.log('Solicitud de soporte:', { tipo: selectedOption, mensaje: message });
    onClose();
  };

  const supportOptions = [
    {
      id: 'technical',
      title: 'Problema Técnico',
      description: 'Issues con la plataforma o funcionalidades',
      icon: HelpCircle,
      color: 'text-red-600'
    },
    {
      id: 'account',
      title: 'Gestión de Cuenta',
      description: 'Configuración, pagos, comisiones',
      icon: Mail,
      color: 'text-blue-600'
    },
    {
      id: 'products',
      title: 'Gestión de Productos',
      description: 'Ayuda con productos y ventas',
      icon: MessageCircle,
      color: 'text-green-600'
    }
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <HelpCircle className="w-6 h-6 text-purple-600" />
            <h2 className="text-xl font-semibold text-gray-900">Contactar Soporte</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6">
          {/* Información de contacto rápido */}
          <div className="mb-6 p-4 bg-purple-50 rounded-lg">
            <h3 className="font-medium text-purple-900 mb-2">Contacto Directo</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center space-x-2">
                <Mail className="w-4 h-4 text-purple-600" />
                <span className="text-purple-800">soporte@mestore.com</span>
              </div>
              <div className="flex items-center space-x-2">
                <Phone className="w-4 h-4 text-purple-600" />
                <span className="text-purple-800">+1 (555) 123-4567</span>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Tipo de consulta */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                ¿En qué podemos ayudarte? *
              </label>
              <div className="space-y-3">
                {supportOptions.map((option) => {
                  const IconComponent = option.icon;
                  return (
                    <label
                      key={option.id}
                      className={`flex items-start space-x-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedOption === option.id
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="supportType"
                        value={option.id}
                        checked={selectedOption === option.id}
                        onChange={(e) => setSelectedOption(e.target.value)}
                        className="mt-1"
                        required
                      />
                      <IconComponent className={`w-5 h-5 mt-0.5 ${option.color}`} />
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{option.title}</h4>
                        <p className="text-sm text-gray-600">{option.description}</p>
                      </div>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Mensaje */}
            <div>
              <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
                Describe tu consulta *
              </label>
              <textarea
                id="message"
                name="message"
                rows={4}
                required
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Explica detalladamente tu consulta o problema..."
              />
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md transition-colors"
              >
                Enviar Consulta
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SoporteModal;
