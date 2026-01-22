"use client";

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface StudyData {
  date: string;
  study_time: number; // in minutes
  tasks_completed: number;
  average_score: number;
}

interface AnalyticsData {
  total_study_time: string;
  average_daily_study: string;
  completion_rate: number;
  strongest_subjects: Array<{ name: string; score: number }>;
  weakest_subjects: Array<{ name: string; score: number }>;
  study_streak: number;
  productivity_trend: 'up' | 'down' | 'stable';
  recommendations: string[];
}

export default function PerformanceAnalytics() {
  const { session } = useAuth();
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [studyData, setStudyData] = useState<StudyData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [session]);

  const fetchAnalytics = async () => {
    if (!session) return;

    setLoading(true);
    try {
      // Aquí cargaríamos estadísticas reales de la API
      // Por ahora, mostrar valores iniciales
      const initialAnalytics: AnalyticsData = {
        total_study_time: "0h 0m",
        average_daily_study: "0h 0m",
        completion_rate: 0,
        strongest_subjects: [],
        weakest_subjects: [],
        study_streak: 0,
        productivity_trend: 'stable',
        recommendations: [
          "¡Comienza agregando tus primeras tareas!",
          "Crea tu primera materia para organizar mejor tus estudios",
          "El sistema de IA te ayudará a estudiar de manera más eficiente"
        ]
      };

      const initialStudyData: StudyData[] = [];

      setAnalytics(initialAnalytics);
      setStudyData(initialStudyData);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !analytics) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="text-center">
                <div className="h-8 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
              </div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 Análisis de Rendimiento</h2>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{analytics.total_study_time}</div>
          <div className="text-sm text-blue-700">Tiempo total estudiado</div>
        </div>
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{analytics.average_daily_study}</div>
          <div className="text-sm text-green-700">Promedio diario</div>
        </div>
        <div className="text-center p-4 bg-purple-50 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">{analytics.completion_rate}%</div>
          <div className="text-sm text-purple-700">Tasa de completación</div>
        </div>
        <div className="text-center p-4 bg-orange-50 rounded-lg">
          <div className="text-2xl font-bold text-orange-600">{analytics.study_streak}</div>
          <div className="text-sm text-orange-700">Días de racha</div>
        </div>
      </div>

      {/* Study Time Chart (Simple visualization) */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Tendencia de Estudio (Últimos 7 días)</h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="flex items-end space-x-2 h-32">
            {studyData.map((day, index) => {
              const height = (day.study_time / 180) * 100; // Max 180 min = 100%
              return (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div
                    className="w-full bg-gradient-to-t from-blue-500 to-blue-600 rounded-t mb-2 transition-all duration-300 hover:from-blue-600 hover:to-blue-700"
                    style={{ height: `${Math.max(height, 5)}%` }}
                  >
                    <div className="text-xs text-white text-center py-1 opacity-0 hover:opacity-100 transition-opacity">
                      {day.study_time}m
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(day.date).toLocaleDateString('es-ES', { weekday: 'short' })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Subject Performance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 text-green-700">🟢 Asignaturas Más Fuertes</h3>
          <div className="space-y-3">
            {analytics.strongest_subjects.map((subject, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="font-medium text-green-900">{subject.name}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-green-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${subject.score}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-semibold text-green-700">{subject.score}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 text-red-700">🔴 Asignaturas a Mejorar</h3>
          <div className="space-y-3">
            {analytics.weakest_subjects.map((subject, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <span className="font-medium text-red-900">{subject.name}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-red-200 rounded-full h-2">
                    <div
                      className="bg-red-600 h-2 rounded-full"
                      style={{ width: `${subject.score}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-semibold text-red-700">{subject.score}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center">
          🤖 Recomendaciones de IA
        </h3>
        <div className="space-y-3">
          {analytics.recommendations.map((recommendation, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                {index + 1}
              </div>
              <p className="text-blue-800">{recommendation}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Productivity Trend */}
      <div className="mt-6 flex items-center justify-between p-4 bg-gray-50 rounded-lg">
        <div>
          <h4 className="font-semibold text-gray-900">Tendencia de Productividad</h4>
          <p className="text-sm text-gray-600">Basado en tus últimas semanas</p>
        </div>
        <div className="flex items-center space-x-2">
          {analytics.productivity_trend === 'up' && (
            <>
              <span className="text-green-600 text-xl">📈</span>
              <span className="text-green-700 font-medium">Mejorando</span>
            </>
          )}
          {analytics.productivity_trend === 'down' && (
            <>
              <span className="text-red-600 text-xl">📉</span>
              <span className="text-red-700 font-medium">Disminuyendo</span>
            </>
          )}
          {analytics.productivity_trend === 'stable' && (
            <>
              <span className="text-blue-600 text-xl">➡️</span>
              <span className="text-blue-700 font-medium">Estable</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}