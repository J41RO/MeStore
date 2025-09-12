import React, { useState, useEffect } from 'react';
import { useCaptcha } from '../../hooks/useCaptcha';

interface MathCaptchaProps {
  onValidationChange: (isValid: boolean) => void;
  className?: string;
}

const MathCaptcha: React.FC<MathCaptchaProps> = ({ onValidationChange, className = '' }) => {
  const { question, correctAnswer, generateNewQuestion } = useCaptcha();
  const [userAnswer, setUserAnswer] = useState('');
  const [isValid, setIsValid] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  useEffect(() => {
    const isAnswerCorrect = parseInt(userAnswer) === correctAnswer;
    setIsValid(isAnswerCorrect);
    onValidationChange(isAnswerCorrect);
    
    if (userAnswer && showFeedback) {
      const timer = setTimeout(() => setShowFeedback(false), 2000);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [userAnswer, correctAnswer, onValidationChange, showFeedback]);

  const handleAnswerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    
    // Only allow numbers
    if (value === '' || /^\d+$/.test(value)) {
      setUserAnswer(value);
      
      // Show feedback when user enters an answer
      if (value && parseInt(value) !== correctAnswer) {
        setShowFeedback(true);
      }
    }
  };

  const handleRefresh = () => {
    generateNewQuestion();
    setUserAnswer('');
    setShowFeedback(false);
  };

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center justify-between">
        <label className="block text-sm font-semibold text-gray-700">
          Verificación de Seguridad *
        </label>
        <button
          type="button"
          onClick={handleRefresh}
          className="text-blue-600 hover:text-blue-800 text-xs font-medium flex items-center transition-colors"
          title="Generar nueva pregunta"
        >
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Nueva pregunta
        </button>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 border-2 border-dashed border-gray-300">
        <div className="flex items-center justify-center space-x-4">
          <div className="text-lg font-mono font-bold text-gray-800 bg-white px-4 py-2 rounded border">
            {question}
          </div>
          <span className="text-lg font-bold text-gray-600">=</span>
          <input
            type="text"
            value={userAnswer}
            onChange={handleAnswerChange}
            className={`w-20 text-center text-lg font-mono font-bold border-2 rounded px-3 py-2 transition-all ${
              userAnswer === ''
                ? 'border-gray-300 focus:border-blue-500'
                : isValid
                ? 'border-green-500 bg-green-50 text-green-700'
                : 'border-red-500 bg-red-50 text-red-700'
            } focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-20`}
            placeholder="?"
            maxLength={4}
          />
        </div>

        {/* Feedback */}
        <div className="mt-3 text-center min-h-[20px]">
          {userAnswer && isValid && (
            <div className="flex items-center justify-center text-green-600 text-sm font-medium">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              ¡Correcto!
            </div>
          )}
          {userAnswer && !isValid && showFeedback && (
            <div className="flex items-center justify-center text-red-600 text-sm font-medium">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              Intenta de nuevo
            </div>
          )}
          {!userAnswer && (
            <div className="text-gray-500 text-sm">
              Resuelve la operación matemática
            </div>
          )}
        </div>
      </div>

      <div className="text-xs text-gray-600 flex items-center">
        <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        Esta verificación nos ayuda a prevenir spam y bots
      </div>
    </div>
  );
};

export default MathCaptcha;