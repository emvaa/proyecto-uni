"use client";

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  points: number;
  unlocked_at: string;
  achievement_type: string;
}

const ACHIEVEMENT_TYPES = [
  {
    type: 'first_task',
    title: 'Primer Paso',
    description: '¡Completaste tu primera tarea!',
    icon: '🎯',
    points: 10
  },
  {
    type: 'study_streak_3',
    title: 'Racha de Estudio',
    description: '3 días seguidos estudiando',
    icon: '🔥',
    points: 25
  },
  {
    type: 'study_streak_7',
    title: 'Semana Perfecta',
    description: '7 días seguidos estudiando',
    icon: '🏆',
    points: 50
  },
  {
    type: 'perfect_quiz',
    title: 'Nota Perfecta',
    description: '100% en un quiz',
    icon: '⭐',
    points: 30
  },
  {
    type: 'early_bird',
    title: 'Madrugador',
    description: 'Estudiaste antes de las 7 AM',
    icon: '🌅',
    points: 15
  },
  {
    type: 'night_owl',
    title: 'Búho Nocturno',
    description: 'Estudiaste después de las 11 PM',
    icon: '🦉',
    points: 15
  },
  {
    type: 'task_master',
    title: 'Maestro de Tareas',
    description: 'Completaste 10 tareas',
    icon: '👑',
    points: 40
  },
  {
    type: 'knowledge_seeker',
    title: 'Buscador del Conocimiento',
    description: 'Generaste 50 flashcards',
    icon: '📚',
    points: 35
  }
];

export default function Achievements() {
  const { session } = useAuth();
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);

  // Cargar logros reales de la API
  useEffect(() => {
    fetchAchievements();
  }, [session]);

  const fetchAchievements = async () => {
    if (!session) return;

    setLoading(true);
    try {
      // Aquí cargaríamos logros reales de la API
      // Por ahora, mostrar lista vacía
      setAchievements([]);
    } catch (error) {
      console.error('Error loading achievements:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalPoints = achievements.reduce((sum, achievement) => sum + achievement.points, 0);
  const unlockedCount = achievements.length;
  const totalCount = ACHIEVEMENT_TYPES.length;

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🏆 Logros</h2>
          <p className="text-gray-600 mt-1">
            {unlockedCount} de {totalCount} logros desbloqueados
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-yellow-600">{totalPoints}</div>
          <div className="text-sm text-gray-500">puntos totales</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progreso general</span>
          <span>{Math.round((unlockedCount / totalCount) * 100)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-yellow-400 to-yellow-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${(unlockedCount / totalCount) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Unlocked Achievements */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Logros Desbloqueados</h3>
        <div className="space-y-4">
          {achievements.map((achievement) => (
            <div key={achievement.id} className="flex items-center space-x-4 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
              <div className="text-3xl">{achievement.icon}</div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{achievement.title}</h4>
                <p className="text-sm text-gray-600">{achievement.description}</p>
                <p className="text-xs text-gray-500 mt-1">
                  Desbloqueado el {new Date(achievement.unlocked_at).toLocaleDateString()}
                </p>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-yellow-600">+{achievement.points}</div>
                <div className="text-xs text-gray-500">puntos</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Available Achievements */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Logros Disponibles</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {ACHIEVEMENT_TYPES.filter(type =>
            !achievements.some(a => a.achievement_type === type.type)
          ).map((achievement) => (
            <div key={achievement.type} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 opacity-60">
              <div className="text-3xl grayscale">{achievement.icon}</div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-700">{achievement.title}</h4>
                <p className="text-sm text-gray-500">{achievement.description}</p>
                <div className="text-xs text-gray-400 mt-1">
                  {achievement.points} puntos
                </div>
              </div>
              <div className="text-gray-400">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Motivational Message */}
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">💪</div>
          <div>
            <h4 className="font-semibold text-blue-900">¡Sigue así!</h4>
            <p className="text-sm text-blue-700">
              Cada tarea completada, cada sesión de estudio, cada logro te acerca más a tus metas académicas.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}