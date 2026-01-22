-- =====================================================
-- UNI AI - DATABASE SCHEMA
-- Ejecutar en Supabase SQL Editor
-- =====================================================

-- =====================================================
-- 1. TABLAS PRINCIPALES
-- =====================================================

-- Tabla de perfiles de usuario (extensión de auth.users)
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    study_preferences JSONB DEFAULT '{
        "study_time_per_day": 2,
        "preferred_study_times": ["morning", "afternoon"],
        "learning_style": "visual",
        "weak_subjects": [],
        "notification_preferences": {
            "email": true,
            "push": true,
            "reminders": true
        }
    }'::jsonb,
    academic_info JSONB DEFAULT '{
        "university": "",
        "major": "",
        "current_semester": 1,
        "gpa": 0.0,
        "study_streak": 0
    }'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabla de materias/cursos
CREATE TABLE public.subjects (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    code TEXT, -- Código de la materia (ej: "MAT101")
    color TEXT DEFAULT '#3b82f6', -- Color para UI
    description TEXT,
    professor TEXT,
    schedule JSONB, -- Horarios de clase
    credits INTEGER DEFAULT 3,
    difficulty_level INTEGER CHECK (difficulty_level >= 1 AND difficulty_level <= 5) DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(user_id, code)
);

-- Tabla de tareas
CREATE TABLE public.tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    subject_id UUID REFERENCES public.subjects(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    task_type TEXT CHECK (task_type IN ('homework', 'exam', 'project', 'reading', 'practice', 'other')) DEFAULT 'homework',
    priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
    status TEXT CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')) DEFAULT 'pending',

    -- Fechas
    due_date TIMESTAMP WITH TIME ZONE,
    estimated_duration INTERVAL, -- Cuánto tiempo se estima que tome
    actual_duration INTERVAL, -- Tiempo real que tomó
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Archivos adjuntos
    attachments JSONB DEFAULT '[]'::jsonb, -- Array de file URLs/IDs

    -- Análisis con IA
    ai_analysis JSONB DEFAULT '{}'::jsonb, -- Análisis del contenido por IA
    ai_explanation JSONB DEFAULT '{}'::jsonb, -- Explicación paso a paso
    ai_solution JSONB DEFAULT '{}'::jsonb, -- Solución propuesta

    -- Metadatos
    tags TEXT[] DEFAULT '{}'::text[],
    progress_percentage INTEGER CHECK (progress_percentage >= 0 AND progress_percentage <= 100) DEFAULT 0,
    notes TEXT, -- Notas personales del estudiante

    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabla de sesiones de estudio
CREATE TABLE public.study_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    subject_id UUID REFERENCES public.subjects(id) ON DELETE SET NULL,
    task_id UUID REFERENCES public.tasks(id) ON DELETE SET NULL,

    title TEXT NOT NULL,
    description TEXT,
    session_type TEXT CHECK (session_type IN ('review', 'practice', 'new_material', 'exam_prep', 'flashcards')) DEFAULT 'practice',

    -- Tiempo y duración
    start_time TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    planned_duration INTERVAL,
    actual_duration INTERVAL,

    -- Contenido estudiado
    topics_covered TEXT[] DEFAULT '{}'::text[],
    difficulty_rating INTEGER CHECK (difficulty_rating >= 1 AND difficulty_rating <= 5),

    -- Estadísticas de la sesión
    flashcards_reviewed INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,

    -- Notas y reflexiones
    notes TEXT,
    what_learned TEXT,
    what_to_improve TEXT,

    -- IA insights
    ai_insights JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabla de flashcards
CREATE TABLE public.flashcards (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    subject_id UUID REFERENCES public.subjects(id) ON DELETE CASCADE NOT NULL,

    front_content TEXT NOT NULL, -- Pregunta o concepto
    back_content TEXT NOT NULL, -- Respuesta o explicación
    card_type TEXT CHECK (card_type IN ('basic', 'multiple_choice', 'true_false', 'image')) DEFAULT 'basic',

    -- Metadatos
    difficulty_level INTEGER CHECK (difficulty_level >= 1 AND difficulty_level <= 5) DEFAULT 3,
    tags TEXT[] DEFAULT '{}'::text[],
    source_task_id UUID REFERENCES public.tasks(id) ON DELETE SET NULL,
    source_material TEXT, -- De dónde viene (PDF, clase, etc.)

    -- Spaced repetition system
    easiness_factor DECIMAL(3,2) DEFAULT 2.5,
    interval_days INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    next_review_date DATE DEFAULT CURRENT_DATE,

    -- Estadísticas
    times_reviewed INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    times_incorrect INTEGER DEFAULT 0,
    last_reviewed_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabla de quizzes generados automáticamente
CREATE TABLE public.quizzes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    subject_id UUID REFERENCES public.subjects(id) ON DELETE CASCADE NOT NULL,
    task_id UUID REFERENCES public.tasks(id) ON DELETE SET NULL,

    title TEXT NOT NULL,
    description TEXT,
    quiz_type TEXT CHECK (quiz_type IN ('practice', 'exam_sim', 'spaced_review', 'weak_topics')) DEFAULT 'practice',

    -- Configuración
    total_questions INTEGER DEFAULT 10,
    time_limit INTERVAL, -- NULL = sin límite
    passing_score DECIMAL(5,2), -- Porcentaje requerido para aprobar

    -- Estadísticas
    questions JSONB DEFAULT '[]'::jsonb, -- Array de preguntas con opciones y respuestas
    generated_by_ai BOOLEAN DEFAULT true,

    -- Resultados
    completed_at TIMESTAMP WITH TIME ZONE,
    score DECIMAL(5,2), -- Porcentaje obtenido
    time_taken INTERVAL,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabla de respuestas a quizzes
CREATE TABLE public.quiz_responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    quiz_id UUID REFERENCES public.quizzes(id) ON DELETE CASCADE NOT NULL,
    question_index INTEGER NOT NULL,
    user_answer TEXT,
    correct_answer TEXT,
    is_correct BOOLEAN NOT NULL,
    time_taken INTERVAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabla de calendario académico
CREATE TABLE public.calendar_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,

    title TEXT NOT NULL,
    description TEXT,
    event_type TEXT CHECK (event_type IN ('class', 'exam', 'deadline', 'study_session', 'reminder', 'other')) DEFAULT 'other',

    -- Fechas y recurrencia
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    is_all_day BOOLEAN DEFAULT false,

    -- Recurrencia (para clases semanales)
    recurrence_rule JSONB, -- RRULE format o custom

    -- Relaciones
    subject_id UUID REFERENCES public.subjects(id) ON DELETE SET NULL,
    task_id UUID REFERENCES public.tasks(id) ON DELETE SET NULL,
    study_session_id UUID REFERENCES public.study_sessions(id) ON DELETE SET NULL,

    -- Notificaciones
    reminder_settings JSONB DEFAULT '{
        "email": true,
        "push": false,
        "minutes_before": 60
    }'::jsonb,

    -- Metadatos
    priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
    status TEXT CHECK (status IN ('scheduled', 'completed', 'cancelled', 'postponed')) DEFAULT 'scheduled',
    color TEXT DEFAULT '#3b82f6',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabla de logros y gamificación
CREATE TABLE public.achievements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,

    achievement_type TEXT NOT NULL, -- "study_streak", "tasks_completed", "perfect_quiz", etc.
    title TEXT NOT NULL,
    description TEXT,
    icon TEXT, -- Emoji o icon name
    points INTEGER DEFAULT 10,

    unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb, -- Datos adicionales del logro

    UNIQUE(user_id, achievement_type, unlocked_at::date)
);

-- Tabla de estadísticas diarias
CREATE TABLE public.daily_stats (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    date DATE DEFAULT CURRENT_DATE,

    -- Tiempos de estudio
    study_time INTERVAL DEFAULT '00:00:00',
    planned_study_time INTERVAL DEFAULT '00:00:00',

    -- Actividad
    tasks_completed INTEGER DEFAULT 0,
    flashcards_reviewed INTEGER DEFAULT 0,
    quizzes_taken INTEGER DEFAULT 0,

    -- Rendimiento
    average_quiz_score DECIMAL(5,2),
    study_streak_days INTEGER DEFAULT 0,

    -- Metadatos
    mood_rating INTEGER CHECK (mood_rating >= 1 AND mood_rating <= 5), -- 1-5 escala de ánimo
    productivity_rating INTEGER CHECK (productivity_rating >= 1 AND productivity_rating <= 5),
    notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,

    UNIQUE(user_id, date)
);

-- =====================================================
-- 2. FUNCIONES Y TRIGGERS
-- =====================================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para updated_at
CREATE TRIGGER handle_updated_at_profiles
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER handle_updated_at_subjects
    BEFORE UPDATE ON public.subjects
    FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER handle_updated_at_tasks
    BEFORE UPDATE ON public.tasks
    FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER handle_updated_at_study_sessions
    BEFORE UPDATE ON public.study_sessions
    FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER handle_updated_at_flashcards
    BEFORE UPDATE ON public.flashcards
    FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER handle_updated_at_quizzes
    BEFORE UPDATE ON public.quizzes
    FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER handle_updated_at_calendar_events
    BEFORE UPDATE ON public.calendar_events
    FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER handle_updated_at_daily_stats
    BEFORE UPDATE ON public.daily_stats
    FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

-- Función para crear perfil automáticamente al registrar usuario
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'avatar_url');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger para crear perfil automáticamente
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- =====================================================
-- 3. POLÍTICAS DE SEGURIDAD (RLS)
-- =====================================================

-- Habilitar RLS en todas las tablas
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flashcards ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.calendar_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_stats ENABLE ROW LEVEL SECURITY;

-- Políticas para profiles (los usuarios solo pueden ver/editar su propio perfil)
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Políticas para subjects
CREATE POLICY "Users can view own subjects" ON public.subjects
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own subjects" ON public.subjects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own subjects" ON public.subjects
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own subjects" ON public.subjects
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para tasks
CREATE POLICY "Users can view own tasks" ON public.tasks
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own tasks" ON public.tasks
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own tasks" ON public.tasks
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own tasks" ON public.tasks
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para study_sessions
CREATE POLICY "Users can view own study sessions" ON public.study_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own study sessions" ON public.study_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own study sessions" ON public.study_sessions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own study sessions" ON public.study_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para flashcards
CREATE POLICY "Users can view own flashcards" ON public.flashcards
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own flashcards" ON public.flashcards
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own flashcards" ON public.flashcards
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own flashcards" ON public.flashcards
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para quizzes
CREATE POLICY "Users can view own quizzes" ON public.quizzes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own quizzes" ON public.quizzes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own quizzes" ON public.quizzes
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own quizzes" ON public.quizzes
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para quiz_responses
CREATE POLICY "Users can view own quiz responses" ON public.quiz_responses
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM public.quizzes WHERE id = quiz_id
        )
    );

CREATE POLICY "Users can insert own quiz responses" ON public.quiz_responses
    FOR INSERT WITH CHECK (
        auth.uid() IN (
            SELECT user_id FROM public.quizzes WHERE id = quiz_id
        )
    );

-- Políticas para calendar_events
CREATE POLICY "Users can view own calendar events" ON public.calendar_events
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own calendar events" ON public.calendar_events
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own calendar events" ON public.calendar_events
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own calendar events" ON public.calendar_events
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para achievements
CREATE POLICY "Users can view own achievements" ON public.achievements
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own achievements" ON public.achievements
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Políticas para daily_stats
CREATE POLICY "Users can view own daily stats" ON public.daily_stats
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own daily stats" ON public.daily_stats
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own daily stats" ON public.daily_stats
    FOR UPDATE USING (auth.uid() = user_id);

-- =====================================================
-- 4. ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================

-- Índices para búsquedas comunes
CREATE INDEX idx_tasks_user_due_date ON public.tasks(user_id, due_date) WHERE status != 'completed';
CREATE INDEX idx_tasks_user_status ON public.tasks(user_id, status);
CREATE INDEX idx_flashcards_user_next_review ON public.flashcards(user_id, next_review_date);
CREATE INDEX idx_study_sessions_user_date ON public.study_sessions(user_id, start_time);
CREATE INDEX idx_calendar_events_user_date ON public.calendar_events(user_id, start_date);
CREATE INDEX idx_daily_stats_user_date ON public.daily_stats(user_id, date);

-- Índices de texto completo para búsquedas
CREATE INDEX idx_tasks_search ON public.tasks USING gin(to_tsvector('spanish', title || ' ' || description));
CREATE INDEX idx_flashcards_search ON public.flashcards USING gin(to_tsvector('spanish', front_content || ' ' || back_content));

-- =====================================================
-- 5. DATOS DE EJEMPLO (OPCIONAL)
-- =====================================================

-- Insertar algunos datos de ejemplo (descomentar si se desea)
/*
-- Materias de ejemplo
INSERT INTO public.subjects (user_id, name, code, color, difficulty_level) VALUES
('user-uuid-aqui', 'Cálculo Diferencial', 'MAT101', '#ef4444', 4),
('user-uuid-aqui', 'Física Mecánica', 'FIS101', '#3b82f6', 3),
('user-uuid-aqui', 'Programación I', 'INF101', '#10b981', 2);

-- Tareas de ejemplo
INSERT INTO public.tasks (user_id, subject_id, title, description, task_type, priority, due_date, estimated_duration) VALUES
('user-uuid-aqui', (SELECT id FROM subjects WHERE code = 'MAT101' LIMIT 1), 'Resolver ejercicios del capítulo 5', 'Ejercicios 5.1 al 5.15 sobre derivadas', 'homework', 'high', NOW() + INTERVAL '3 days', INTERVAL '2 hours');
*/

-- =====================================================
-- 5. SISTEMA DE CHATS SEPARADOS
-- =====================================================

-- Tabla de chats (uno por tarea + chat general)
CREATE TABLE public.chats (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    task_id UUID REFERENCES public.tasks(id) ON DELETE CASCADE, -- NULL para chat general
    subject_id UUID REFERENCES public.subjects(id) ON DELETE SET NULL,

    title TEXT NOT NULL,
    chat_type TEXT CHECK (chat_type IN ('general', 'task')) DEFAULT 'general',
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabla de mensajes de chat
CREATE TABLE public.chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    chat_id UUID REFERENCES public.chats(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,

    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    message_type TEXT DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file')),

    -- Metadata de IA
    tokens_used INTEGER,
    model_used TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- 6. FUNCIONES Y TRIGGERS ADICIONALES
-- =====================================================

-- Función para crear chat automáticamente cuando se crea una tarea
CREATE OR REPLACE FUNCTION public.handle_new_task_chat()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.chats (user_id, task_id, subject_id, title, chat_type)
    VALUES (NEW.user_id, NEW.id, NEW.subject_id, 'Chat: ' || NEW.title, 'task');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger para crear chat de tarea automáticamente
CREATE TRIGGER create_task_chat
    AFTER INSERT ON public.tasks
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_task_chat();

-- Función para crear chat general automáticamente cuando se crea un usuario
CREATE OR REPLACE FUNCTION public.handle_new_user_general_chat()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.chats (user_id, title, chat_type)
    VALUES (NEW.id, 'Chat General', 'general');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger para crear chat general automáticamente
CREATE TRIGGER create_general_chat
    AFTER INSERT ON public.profiles
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user_general_chat();

-- =====================================================
-- 7. POLÍTICAS DE SEGURIDAD PARA CHATS
-- =====================================================

-- Habilitar RLS en las nuevas tablas
ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

-- Políticas para chats
CREATE POLICY "Users can view own chats" ON public.chats
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chats" ON public.chats
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own chats" ON public.chats
    FOR UPDATE USING (auth.uid() = user_id);

-- Políticas para mensajes de chat
CREATE POLICY "Users can view messages from own chats" ON public.chat_messages
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM public.chats WHERE id = chat_id
        )
    );

CREATE POLICY "Users can insert messages in own chats" ON public.chat_messages
    FOR INSERT WITH CHECK (
        auth.uid() = user_id AND
        auth.uid() IN (
            SELECT user_id FROM public.chats WHERE id = chat_id
        )
    );

-- =====================================================
-- 8. ÍNDICES ADICIONALES
-- =====================================================

-- Índices para chats
CREATE INDEX idx_chats_user_type ON public.chats(user_id, chat_type);
CREATE INDEX idx_chats_task ON public.chats(task_id) WHERE task_id IS NOT NULL;
CREATE INDEX idx_chat_messages_chat_created ON public.chat_messages(chat_id, created_at);

-- =====================================================
-- FIN DEL SCHEMA ACTUALIZADO
-- =====================================================

-- Notas importantes:
-- 1. Reemplaza 'user-uuid-aqui' con UUIDs reales cuando insertes datos de ejemplo
-- 2. Asegúrate de que las funciones y triggers estén habilitados
-- 3. Verifica que las políticas RLS estén funcionando correctamente
-- 4. Considera configurar backups automáticos para la base de datos
-- 5. Los chats se crean automáticamente para cada tarea nueva
-- 6. Hay un chat general por usuario que se crea automáticamente