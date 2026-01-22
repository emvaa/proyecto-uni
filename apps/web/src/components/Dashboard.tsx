"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/lib/supabase';
import TaskList from './TaskList';
import Achievements from './Achievements';
import PerformanceAnalytics from './PerformanceAnalytics';
import StudySystem from './StudySystem';
import SubjectsManager from './SubjectsManager';

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function Dashboard() {
  const { user, signOut, session } = useAuth();
  const [activeTab, setActiveTab] = useState<'chat' | 'tasks' | 'subjects' | 'study' | 'analytics' | 'achievements'>('chat');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<"learn" | "review">("learn");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Test endpoint without authentication
      console.log('Testing chat endpoint without authentication');

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          message: input,
          mode: mode,
        }),
      });

      if (!response.ok) {
        let errorMessage = `Error: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (parseError) {
          // If we can't parse the error response, use the status
          console.error('Failed to parse error response:', parseError);
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Lo siento, hubo un error al procesar tu mensaje: ${error instanceof Error ? error.message : 'Error desconocido'}. Por favor, inténtalo de nuevo.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">UniAI</h1>
          <p className="text-sm text-gray-600 mt-1">Tu asistente universitario</p>
          {user && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm font-medium text-blue-900">Usuario conectado</p>
              <p className="text-xs text-blue-700 truncate">{user.email}</p>
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="p-4 border-b border-gray-200">
          <nav className="grid grid-cols-6 gap-1">
            <button
              onClick={() => setActiveTab('chat')}
              className={`py-2 px-2 text-xs font-medium rounded-lg transition-colors ${
                activeTab === 'chat'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              💬 Chat
            </button>
            <button
              onClick={() => setActiveTab('subjects')}
              className={`py-2 px-2 text-xs font-medium rounded-lg transition-colors ${
                activeTab === 'subjects'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              📚 Materias
            </button>
            <button
              onClick={() => setActiveTab('tasks')}
              className={`py-2 px-2 text-xs font-medium rounded-lg transition-colors ${
                activeTab === 'tasks'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              📋 Tareas
            </button>
            <button
              onClick={() => setActiveTab('study')}
              className={`py-2 px-2 text-xs font-medium rounded-lg transition-colors ${
                activeTab === 'study'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              🎓 Estudio
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`py-2 px-2 text-xs font-medium rounded-lg transition-colors ${
                activeTab === 'analytics'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              📊 Analytics
            </button>
            <button
              onClick={() => setActiveTab('achievements')}
              className={`py-2 px-2 text-xs font-medium rounded-lg transition-colors ${
                activeTab === 'achievements'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              🏆 Logros
            </button>
          </nav>
        </div>

        {/* Tab-specific sidebar content */}
        {activeTab === 'chat' && (
          <div className="p-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Modo de aprendizaje
                </label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setMode("learn")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      mode === "learn"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    Aprender
                  </button>
                  <button
                    onClick={() => setMode("review")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      mode === "review"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    Repasar
                  </button>
                </div>
              </div>

              <div className="text-xs text-gray-500">
                <p><strong>Modo Aprender:</strong> Te guía paso a paso con pistas</p>
                <p className="mt-1"><strong>Modo Repasar:</strong> Resume y hace preguntas rápidas</p>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Historial de conversación</h3>
              <div className="space-y-2">
                {messages.length === 0 ? (
                  <p className="text-sm text-gray-500">No hay mensajes aún</p>
                ) : (
                  messages.slice(-5).map((msg, index) => (
                    <div
                      key={msg.id}
                      className="text-xs text-gray-600 truncate bg-gray-50 p-2 rounded"
                    >
                      {msg.role === "user" ? "Tú:" : "IA:"} {msg.content.substring(0, 40)}...
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'subjects' && (
          <div className="p-6">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Materias Registradas</h3>
            <div className="space-y-3">
              <div className="bg-blue-50 p-3 rounded-lg">
                <div className="text-lg font-semibold text-blue-900">0</div>
                <div className="text-xs text-blue-700">Materias activas</div>
              </div>
              <div className="bg-green-50 p-3 rounded-lg">
                <div className="text-lg font-semibold text-green-900">0</div>
                <div className="text-xs text-green-700">Créditos totales</div>
              </div>
            </div>

            <div className="mt-4">
              <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm">
                + Nueva Materia
              </button>
            </div>
          </div>
        )}

        {activeTab === 'tasks' && (
          <div className="p-6">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Estadísticas Rápidas</h3>
            <div className="space-y-3">
              <div className="bg-blue-50 p-3 rounded-lg">
                <div className="text-lg font-semibold text-blue-900">0</div>
                <div className="text-xs text-blue-700">Tareas completadas hoy</div>
              </div>
              <div className="bg-orange-50 p-3 rounded-lg">
                <div className="text-lg font-semibold text-orange-900">0</div>
                <div className="text-xs text-orange-700">Tareas pendientes</div>
              </div>
              <div className="bg-green-50 p-3 rounded-lg">
                <div className="text-lg font-semibold text-green-900">0%</div>
                <div className="text-xs text-green-700">Tasa de completación</div>
              </div>
            </div>

            <div className="mt-4">
              <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm">
                + Nueva Tarea
              </button>
            </div>
          </div>
        )}

        {activeTab === 'study' && (
          <div className="p-6">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Sesión Actual</h3>
            <div className="space-y-3">
              <div className="bg-green-50 p-3 rounded-lg">
                <div className="text-lg font-semibold text-green-900">00:00</div>
                <div className="text-xs text-green-700">Tiempo estudiando</div>
              </div>
              <div className="bg-purple-50 p-3 rounded-lg">
                <div className="text-lg font-semibold text-purple-900">0</div>
                <div className="text-xs text-purple-700">Flashcards repasadas</div>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <button className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors text-sm">
                ▶️ Continuar Estudiando
              </button>
              <button className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors text-sm">
                ⏹️ Pausar Sesión
              </button>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="p-6">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Métricas Clave</h3>
            <div className="space-y-3">
              <div className="bg-yellow-50 p-3 rounded-lg">
                <div className="text-lg font-semibold text-yellow-900">0</div>
                <div className="text-xs text-yellow-700">Días de racha</div>
              </div>
              <div className="bg-indigo-50 p-3 rounded-lg">
                <div className="text-lg font-semibold text-indigo-900">0h</div>
                <div className="text-xs text-indigo-700">Tiempo total este mes</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'achievements' && (
          <div className="p-6">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Progreso</h3>
            <div className="space-y-3">
              <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 p-3 rounded-lg">
                <div className="text-lg font-semibold text-yellow-900">0</div>
                <div className="text-xs text-yellow-700">Puntos totales</div>
              </div>
              <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-3 rounded-lg">
                <div className="text-lg font-semibold text-purple-900">0/10</div>
                <div className="text-xs text-purple-700">Logros desbloqueados</div>
              </div>
            </div>

            <div className="mt-4">
              <div className="text-xs text-gray-500 mb-2">Próximo logro:</div>
              <div className="bg-gray-50 p-2 rounded text-xs text-gray-700">
                🎯 Completa tu primera tarea
              </div>
            </div>
          </div>
        )}

        <div className="flex-1"></div>

        <div className="p-6 border-t border-gray-200">
          <button
            onClick={signOut}
            className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Cerrar sesión
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {activeTab === 'chat' && `Chat con IA - Modo ${mode === "learn" ? "Aprender" : "Repasar"}`}
            {activeTab === 'subjects' && 'Gestión de Materias'}
            {activeTab === 'tasks' && 'Gestión de Tareas'}
            {activeTab === 'study' && 'Sistema de Estudio Inteligente'}
            {activeTab === 'analytics' && 'Análisis de Rendimiento'}
            {activeTab === 'achievements' && 'Logros y Gamificación'}
          </h2>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'chat' && (
            <div className="h-full flex flex-col">
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        ¡Bienvenido a UniAI!
                      </h3>
                      <p className="text-gray-600">
                        Comienza preguntando algo sobre tus estudios. Estoy aquí para ayudarte.
                      </p>
                    </div>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.role === "user"
                            ? "bg-blue-600 text-white"
                            : "bg-gray-200 text-gray-900"
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <p className={`text-xs mt-1 ${message.role === "user" ? "text-blue-200" : "text-gray-500"}`}>
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))
                )}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-200 text-gray-900 px-4 py-2 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                        </div>
                        <span className="text-sm">Pensando...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="bg-white border-t border-gray-200 p-6">
                <form onSubmit={sendMessage} className="flex space-x-4">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Escribe tu pregunta aquí..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isLoading}
                  />
                  <button
                    type="submit"
                    disabled={!input.trim() || isLoading}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isLoading ? "Enviando..." : "Enviar"}
                  </button>
                </form>
              </div>
            </div>
          )}

          {activeTab === 'subjects' && (
            <div className="p-6">
              <SubjectsManager />
            </div>
          )}

          {activeTab === 'tasks' && (
            <div className="p-6">
              <TaskList />
            </div>
          )}

          {activeTab === 'study' && (
            <div className="p-6">
              <StudySystem />
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="p-6">
              <PerformanceAnalytics />
            </div>
          )}

          {activeTab === 'achievements' && (
            <div className="p-6">
              <Achievements />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}