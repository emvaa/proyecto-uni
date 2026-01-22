"use client";

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface Flashcard {
  id: string;
  front: string;
  back: string;
  difficulty_level: number;
  next_review_date: string;
  times_reviewed: number;
  times_correct: number;
}

interface Quiz {
  id: string;
  title: string;
  questions: Array<{
    question: string;
    options: string[];
    correct_answer: string;
    explanation: string;
  }>;
}

export default function StudySystem() {
  const { session } = useAuth();
  const [activeTab, setActiveTab] = useState<'flashcards' | 'quizzes' | 'sessions'>('flashcards');
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [currentCard, setCurrentCard] = useState<Flashcard | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(false);

  // Cargar datos reales de la API
  useEffect(() => {
    fetchStudyData();
  }, [session]);

  const fetchStudyData = async () => {
    if (!session) return;

    setLoading(true);
    try {
      // Aquí cargaríamos flashcards y quizzes reales de la API
      // Por ahora, mostrar mensaje de que no hay datos
      setFlashcards([]);
      setQuizzes([]);
      setCurrentCard(null);
    } catch (error) {
      console.error('Error loading study data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFlashcardResponse = (correct: boolean) => {
    if (!currentCard) return;

    // Spaced repetition logic
    const updatedCard = { ...currentCard };
    updatedCard.times_reviewed += 1;
    if (correct) {
      updatedCard.times_correct += 1;
    }

    // Calculate next review date based on performance
    const today = new Date();
    const correctRate = updatedCard.times_correct / updatedCard.times_reviewed;
    const interval = correct ? Math.max(1, updatedCard.difficulty_level * correctRate * 2) : 1;

    today.setDate(today.getDate() + interval);
    updatedCard.next_review_date = today.toISOString().split('T')[0];

    setFlashcards(prev => prev.map(card =>
      card.id === currentCard.id ? updatedCard : card
    ));

    // Move to next card
    const currentIndex = flashcards.findIndex(card => card.id === currentCard.id);
    const nextIndex = (currentIndex + 1) % flashcards.length;
    setCurrentCard(flashcards[nextIndex]);
    setShowAnswer(false);
  };

  const generateQuiz = async (subject: string, difficulty: number) => {
    setLoading(true);
    try {
      // Mock quiz generation - in real app, call AI service
      const newQuiz: Quiz = {
        id: Date.now().toString(),
        title: `Quiz de ${subject} - Nivel ${difficulty}`,
        questions: [
          {
            question: `Pregunta generada automáticamente sobre ${subject}`,
            options: ['Opción A', 'Opción B', 'Opción C', 'Opción D'],
            correct_answer: 'Opción A',
            explanation: 'Esta es una explicación generada por IA.'
          }
        ]
      };
      setQuizzes(prev => [...prev, newQuiz]);
    } catch (error) {
      console.error('Error generating quiz:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">🎓 Sistema de Estudio Inteligente</h2>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        <button
          onClick={() => setActiveTab('flashcards')}
          className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
            activeTab === 'flashcards'
              ? 'bg-white text-blue-600 shadow'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          🃏 Flashcards
        </button>
        <button
          onClick={() => setActiveTab('quizzes')}
          className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
            activeTab === 'quizzes'
              ? 'bg-white text-blue-600 shadow'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          📝 Quizzes
        </button>
        <button
          onClick={() => setActiveTab('sessions')}
          className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
            activeTab === 'sessions'
              ? 'bg-white text-blue-600 shadow'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          ⏱️ Sesiones
        </button>
      </div>

      {/* Flashcards Tab */}
      {activeTab === 'flashcards' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Repaso Espaciado</h3>
            <div className="text-sm text-gray-600">
              {flashcards.filter(card => new Date(card.next_review_date) <= new Date()).length} tarjetas pendientes
            </div>
          </div>

          {currentCard ? (
            <div className="max-w-md mx-auto">
              <div
                className="bg-gradient-to-br from-blue-500 to-purple-600 text-white p-8 rounded-xl shadow-lg cursor-pointer transform transition-transform hover:scale-105"
                onClick={() => setShowAnswer(!showAnswer)}
              >
                <div className="text-center">
                  {!showAnswer ? (
                    <>
                      <div className="text-6xl mb-4">💭</div>
                      <h4 className="text-xl font-bold mb-2">Pregunta</h4>
                      <p className="text-lg">{currentCard.front}</p>
                      <div className="mt-6 text-sm opacity-75">
                        Toca para ver la respuesta
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="text-6xl mb-4">💡</div>
                      <h4 className="text-xl font-bold mb-2">Respuesta</h4>
                      <p className="text-lg">{currentCard.back}</p>
                      <div className="mt-6 text-sm opacity-75">
                        ¿Lo sabías correctamente?
                      </div>
                    </>
                  )}
                </div>
              </div>

              {showAnswer && (
                <div className="flex space-x-4 mt-6">
                  <button
                    onClick={() => handleFlashcardResponse(false)}
                    className="flex-1 bg-red-600 text-white py-3 px-6 rounded-lg hover:bg-red-700 transition-colors font-medium"
                  >
                    ❌ No lo sabía
                  </button>
                  <button
                    onClick={() => handleFlashcardResponse(true)}
                    className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition-colors font-medium"
                  >
                    ✅ Lo sabía
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                ¡Todas las tarjetas estudiadas!
              </h3>
              <p className="text-gray-600">
                Vuelve mañana para más tarjetas de repaso.
              </p>
            </div>
          )}

          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">💡 Sobre el Repaso Espaciado</h4>
            <p className="text-sm text-blue-800">
              Esta técnica científica optimiza el aprendizaje al mostrar las tarjetas en intervalos crecientes,
              moviendo la información de la memoria a corto plazo a la memoria a largo plazo.
            </p>
          </div>
        </div>
      )}

      {/* Quizzes Tab */}
      {activeTab === 'quizzes' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Evaluaciones Generadas por IA</h3>
            <button
              onClick={() => generateQuiz('Matemáticas', 2)}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Generando...' : '+ Nuevo Quiz'}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {quizzes.map((quiz) => (
              <div key={quiz.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <h4 className="font-semibold text-gray-900 mb-2">{quiz.title}</h4>
                <p className="text-sm text-gray-600 mb-3">
                  {quiz.questions.length} preguntas
                </p>
                <div className="flex space-x-2">
                  <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                    ▶️ Comenzar
                  </button>
                  <button className="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700">
                    👁️ Vista previa
                  </button>
                </div>
              </div>
            ))}
          </div>

          {quizzes.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No hay quizzes disponibles
              </h3>
              <p className="text-gray-600 mb-4">
                Genera tu primer quiz personalizado con IA
              </p>
              <button
                onClick={() => generateQuiz('General', 2)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
              >
                Generar Quiz de Prueba
              </button>
            </div>
          )}
        </div>
      )}

      {/* Study Sessions Tab */}
      {activeTab === 'sessions' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Sesiones de Estudio</h3>
            <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
              + Nueva Sesión
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">2h 30m</div>
              <div className="text-sm text-blue-700">Tiempo hoy</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">5</div>
              <div className="text-sm text-green-700">Racha actual</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-purple-600">12</div>
              <div className="text-sm text-purple-700">Sesiones este mes</div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-3">💡 Recomendación de IA</h4>
            <p className="text-gray-700 mb-3">
              Basado en tu rendimiento, te recomendamos dedicar 45 minutos diarios a repasar flashcards
              y 30 minutos a práctica de problemas.
            </p>
            <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 text-sm">
              ⏱️ Iniciar Sesión Recomendada
            </button>
          </div>

          <div className="space-y-3">
            <h4 className="font-semibold text-gray-900">Sesiones Recientes</h4>
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">Sesión de Matemáticas</div>
                  <div className="text-sm text-gray-600">Hace {i} horas • 45 minutos</div>
                </div>
                <div className="text-green-600 font-medium">Completada ✓</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}