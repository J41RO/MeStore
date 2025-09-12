import { useState, useCallback, useEffect } from 'react';

interface CaptchaQuestion {
  question: string;
  answer: number;
}

export const useCaptcha = () => {
  const [currentQuestion, setCurrentQuestion] = useState<CaptchaQuestion>({ question: '', answer: 0 });

  // Generate different types of math questions
  const generateQuestion = useCallback((): CaptchaQuestion => {
    const questionTypes = [
      // Simple addition
      () => {
        const a = Math.floor(Math.random() * 20) + 1;
        const b = Math.floor(Math.random() * 20) + 1;
        return { question: `${a} + ${b}`, answer: a + b };
      },
      // Simple subtraction (ensure positive result)
      () => {
        const a = Math.floor(Math.random() * 30) + 10;
        const b = Math.floor(Math.random() * (a - 1)) + 1;
        return { question: `${a} - ${b}`, answer: a - b };
      },
      // Simple multiplication (small numbers)
      () => {
        const a = Math.floor(Math.random() * 10) + 1;
        const b = Math.floor(Math.random() * 10) + 1;
        return { question: `${a} × ${b}`, answer: a * b };
      },
      // Division with whole numbers
      () => {
        const b = Math.floor(Math.random() * 10) + 2;
        const answer = Math.floor(Math.random() * 10) + 1;
        const a = b * answer;
        return { question: `${a} ÷ ${b}`, answer: answer };
      },
      // Mixed operations
      () => {
        const a = Math.floor(Math.random() * 10) + 1;
        const b = Math.floor(Math.random() * 10) + 1;
        const c = Math.floor(Math.random() * 5) + 1;
        return { question: `${a} + ${b} - ${c}`, answer: a + b - c };
      },
      // Simple squares
      () => {
        const a = Math.floor(Math.random() * 8) + 1;
        return { question: `${a}²`, answer: a * a };
      }
    ];

    const randomType = questionTypes[Math.floor(Math.random() * questionTypes.length)];
    return randomType?.() || { question: '2 + 2', answer: 4 };
  }, []);

  const generateNewQuestion = useCallback(() => {
    const newQuestion = generateQuestion();
    setCurrentQuestion(newQuestion);
  }, [generateQuestion]);

  // Generate initial question on mount
  useEffect(() => {
    generateNewQuestion();
  }, [generateNewQuestion]);

  return {
    question: currentQuestion.question,
    correctAnswer: currentQuestion.answer,
    generateNewQuestion
  };
};