import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { Button } from '../../ui/Button';

interface DocumentsStepProps {
  onNext: () => void;
  onPrev: () => void;
  onComplete: () => void;
  isLoading: boolean;
}

interface DocumentFile {
  file: File;
  preview: string;
  type: 'cedula' | 'rut' | 'certificado_bancario' | 'other';
  uploaded: boolean;
}

const DOCUMENT_TYPES = [
  {
    id: 'cedula',
    name: 'Cédula de Ciudadanía',
    description: 'Ambos lados, legible',
    icon: '🆔',
    required: true
  },
  {
    id: 'rut',
    name: 'RUT (Persona Jurídica)',
    description: 'Solo para empresas',
    icon: '📋',
    required: false
  },
  {
    id: 'certificado_bancario',
    name: 'Certificado Bancario',
    description: 'Para pagos y transferencias',
    icon: '🏦',
    required: true
  }
];

export const DocumentsStep: React.FC<DocumentsStepProps> = ({
  onNext,
  onPrev,
  onComplete,
  isLoading
}) => {
  const [documents, setDocuments] = useState<DocumentFile[]>([]);
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({});
  const [skipDocuments, setSkipDocuments] = useState(false);

  // File validation
  const validateFile = (file: File): { valid: boolean; error?: string } => {
    const maxSize = 5 * 1024 * 1024; // 5MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];

    if (file.size > maxSize) {
      return { valid: false, error: 'Archivo muy grande (máx. 5MB)' };
    }

    if (!allowedTypes.includes(file.type)) {
      return { valid: false, error: 'Tipo de archivo no válido (JPG, PNG, WebP, PDF)' };
    }

    return { valid: true };
  };

  // Handle file drop
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newDocuments: DocumentFile[] = [];

    acceptedFiles.forEach((file) => {
      const validation = validateFile(file);
      if (validation.valid) {
        const documentFile: DocumentFile = {
          file,
          preview: URL.createObjectURL(file),
          type: 'other',
          uploaded: false
        };
        newDocuments.push(documentFile);
      } else {
        alert(`${file.name}: ${validation.error}`);
      }
    });

    setDocuments(prev => [...prev, ...newDocuments]);

    // Simulate upload for each file
    newDocuments.forEach((doc, index) => {
      simulateUpload(doc.file.name, index);
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 10,
    multiple: true
  });

  // Simulate file upload
  const simulateUpload = async (fileName: string, index: number) => {
    setUploadProgress(prev => ({ ...prev, [fileName]: 0 }));

    // Simulate upload progress
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 100));
      setUploadProgress(prev => ({ ...prev, [fileName]: progress }));
    }

    // Mark as uploaded
    setDocuments(prev => prev.map((doc, i) =>
      i === index ? { ...doc, uploaded: true } : doc
    ));

    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[fileName];
      return newProgress;
    });
  };

  // Remove document
  const removeDocument = (index: number) => {
    setDocuments(prev => {
      const newDocs = [...prev];
      URL.revokeObjectURL(newDocs[index].preview);
      newDocs.splice(index, 1);
      return newDocs;
    });
  };

  // Handle completion
  const handleComplete = async () => {
    if (documents.length === 0 && !skipDocuments) {
      const confirmed = window.confirm(
        '¿Estás seguro de que quieres continuar sin subir documentos? Podrás hacerlo después desde tu panel de control.'
      );
      if (!confirmed) return;
    }

    await onComplete();
  };

  const hasRequiredDocuments = documents.some(doc => doc.uploaded);
  const canProceed = hasRequiredDocuments || skipDocuments;

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
          Documentos de Verificación
        </h3>
        <p className="text-gray-600 text-sm">
          Sube los documentos para verificar tu identidad
        </p>
      </div>

      {/* Document Requirements */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h4 className="font-medium text-blue-900 mb-3">📋 Documentos requeridos:</h4>
        <div className="space-y-2">
          {DOCUMENT_TYPES.map((docType) => (
            <div key={docType.id} className="flex items-center space-x-3">
              <span className="text-lg">{docType.icon}</span>
              <div className="flex-1">
                <span className="text-sm font-medium text-blue-900">
                  {docType.name}
                  {docType.required && <span className="text-red-500 ml-1">*</span>}
                </span>
                <p className="text-xs text-blue-700">{docType.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
        }`}
        data-testid="document-upload"
      >
        <input {...getInputProps()} />
        <div className="space-y-4">
          <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <div>
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive ? 'Suelta los archivos aquí' : 'Arrastra archivos o haz clic para seleccionar'}
            </h4>
            <p className="text-sm text-gray-600">
              JPG, PNG, WebP o PDF (máx. 5MB cada uno)
            </p>
          </div>
        </div>
      </div>

      {/* Uploaded Documents */}
      {documents.length > 0 && (
        <div className="space-y-3">
          <h4 className="font-medium text-gray-900">Documentos subidos:</h4>
          {documents.map((doc, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white border border-gray-200 rounded-lg p-4 flex items-center space-x-4"
            >
              {/* File Preview */}
              <div className="flex-shrink-0">
                {doc.file.type.startsWith('image/') ? (
                  <img
                    src={doc.preview}
                    alt={doc.file.name}
                    className="w-12 h-12 object-cover rounded-lg"
                  />
                ) : (
                  <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                    <span className="text-red-600 text-xl">📄</span>
                  </div>
                )}
              </div>

              {/* File Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {doc.file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {(doc.file.size / 1024 / 1024).toFixed(2)} MB
                </p>

                {/* Upload Progress */}
                {uploadProgress[doc.file.name] !== undefined && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-1">
                      <div
                        className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress[doc.file.name]}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Status */}
              <div className="flex-shrink-0 flex items-center space-x-2">
                {doc.uploaded ? (
                  <div className="flex items-center text-green-600">
                    <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-xs font-medium">Subido</span>
                  </div>
                ) : (
                  <div className="flex items-center text-blue-600">
                    <svg className="animate-spin w-4 h-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="text-xs font-medium">Subiendo...</span>
                  </div>
                )}

                {/* Remove Button */}
                <button
                  onClick={() => removeDocument(index)}
                  className="text-red-500 hover:text-red-700 p-1"
                  title="Eliminar archivo"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Skip Option */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <svg className="w-5 h-5 text-yellow-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 18.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium text-yellow-900 mb-1">
                  ¿No tienes los documentos a mano?
                </h4>
                <p className="text-sm text-yellow-700">
                  Puedes subir los documentos después desde tu panel de control.
                </p>
              </div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={skipDocuments}
                  onChange={(e) => setSkipDocuments(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-yellow-900">Subir después</span>
              </label>
            </div>
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
          disabled={isLoading}
        >
          Atrás
        </Button>
        <Button
          onClick={handleComplete}
          disabled={!canProceed || isLoading}
          className="flex-1"
          data-testid="complete-registration"
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Completando registro...
            </div>
          ) : (
            '🎉 Completar Registro'
          )}
        </Button>
      </div>

      {/* Final Tips */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <svg className="w-5 h-5 text-green-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1">
            <h4 className="text-sm font-medium text-green-900 mb-1">
              🚀 ¡Ya casi terminas!
            </h4>
            <p className="text-sm text-green-700">
              Una vez completado el registro, podrás acceder a tu panel de vendedor y comenzar a vender inmediatamente.
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};