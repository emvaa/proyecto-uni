from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Table, Date, Interval
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

# =====================================================
# TABLAS PRINCIPALES
# =====================================================

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), primary_key=True)
    email = Column(String, nullable=False, unique=True)
    full_name = Column(String)
    avatar_url = Column(String)
    study_preferences = Column(JSONB, default=dict)
    academic_info = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    subjects = relationship("Subject", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")
    flashcards = relationship("Flashcard", back_populates="user")
    quizzes = relationship("Quiz", back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")
    achievements = relationship("Achievement", back_populates="user")
    daily_stats = relationship("DailyStats", back_populates="user")
    chats = relationship("Chat", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String)
    color = Column(String, default="#3b82f6")
    description = Column(Text)
    professor = Column(String)
    schedule = Column(JSONB)
    credits = Column(Integer, default=3)
    difficulty_level = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("Profile", back_populates="subjects")
    tasks = relationship("Task", back_populates="subject")
    flashcards = relationship("Flashcard", back_populates="subject")
    quizzes = relationship("Quiz", back_populates="subject")
    study_sessions = relationship("StudySession", back_populates="subject")

    __table_args__ = (
        {'schema': 'public'}
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    task_type = Column(String, default="homework")
    priority = Column(String, default="medium")
    status = Column(String, default="pending")

    # Fechas
    due_date = Column(DateTime)
    estimated_duration = Column(Interval)
    actual_duration = Column(Interval)
    completed_at = Column(DateTime)

    # Archivos adjuntos
    attachments = Column(JSONB, default=list)

    # Análisis con IA
    ai_analysis = Column(JSONB, default=dict)
    ai_explanation = Column(JSONB, default=dict)
    ai_solution = Column(JSONB, default=dict)

    # Metadatos
    tags = Column(ARRAY(String), default=list)
    progress_percentage = Column(Integer, default=0)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("Profile", back_populates="tasks")
    subject = relationship("Subject", back_populates="tasks")
    study_sessions = relationship("StudySession", back_populates="task")
    chat = relationship("Chat", back_populates="task", uselist=False)

    __table_args__ = (
        {'schema': 'public'}
    )


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))

    title = Column(String, nullable=False)
    description = Column(Text)
    session_type = Column(String, default="practice")

    # Tiempo y duración
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime)
    planned_duration = Column(Interval)
    actual_duration = Column(Interval)

    # Contenido estudiado
    topics_covered = Column(ARRAY(String), default=list)
    difficulty_rating = Column(Integer)

    # Estadísticas de la sesión
    flashcards_reviewed = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)

    # Notas y reflexiones
    notes = Column(Text)
    what_learned = Column(Text)
    what_to_improve = Column(Text)

    # IA insights
    ai_insights = Column(JSONB, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("Profile", back_populates="study_sessions")
    subject = relationship("Subject", back_populates="study_sessions")
    task = relationship("Task", back_populates="study_sessions")

    __table_args__ = (
        {'schema': 'public'}
    )


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)

    front_content = Column(Text, nullable=False)
    back_content = Column(Text, nullable=False)
    card_type = Column(String, default="basic")

    # Metadatos
    difficulty_level = Column(Integer, default=3)
    tags = Column(ARRAY(String), default=list)
    source_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    source_material = Column(String)

    # Spaced repetition system
    easiness_factor = Column(Float, default=2.5)
    interval_days = Column(Integer, default=1)
    repetitions = Column(Integer, default=0)
    next_review_date = Column(Date, default=datetime.utcnow().date)

    # Estadísticas
    times_reviewed = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    times_incorrect = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("Profile", back_populates="flashcards")
    subject = relationship("Subject", back_populates="flashcards")

    __table_args__ = (
        {'schema': 'public'}
    )


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))

    title = Column(String, nullable=False)
    description = Column(Text)
    quiz_type = Column(String, default="practice")

    # Configuración
    total_questions = Column(Integer, default=10)
    time_limit = Column(Interval)
    passing_score = Column(Float)

    # Estadísticas
    questions = Column(JSONB, default=list)
    generated_by_ai = Column(Boolean, default=True)

    # Resultados
    completed_at = Column(DateTime)
    score = Column(Float)
    time_taken = Column(Interval)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("Profile", back_populates="quizzes")
    subject = relationship("Subject", back_populates="quizzes")

    __table_args__ = (
        {'schema': 'public'}
    )


class Chat(Base):
    __tablename__ = "chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))  # NULL para chat general
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"))

    title = Column(String, nullable=False)
    chat_type = Column(String, default="general")  # "general" or "task"
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("Profile", back_populates="chats")
    task = relationship("Task", back_populates="chat")
    messages = relationship("ChatMessage", back_populates="chat")

    __table_args__ = (
        {'schema': 'public'}
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)

    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # "text", "image", "file"

    # Metadata
    tokens_used = Column(Integer)
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    chat = relationship("Chat", back_populates="messages")
    user = relationship("Profile", back_populates="chat_messages")

    __table_args__ = (
        {'schema': 'public'}
    )


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text)
    event_type = Column(String, default="other")

    # Fechas y recurrencia
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    is_all_day = Column(Boolean, default=False)

    # Recurrencia
    recurrence_rule = Column(JSONB)

    # Relaciones
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    study_session_id = Column(UUID(as_uuid=True), ForeignKey("study_sessions.id"))

    # Notificaciones
    reminder_settings = Column(JSONB, default=dict)

    # Metadatos
    priority = Column(String, default="medium")
    status = Column(String, default="scheduled")
    color = Column(String, default="#3b82f6")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("Profile", back_populates="calendar_events")

    __table_args__ = (
        {'schema': 'public'}
    )


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)

    achievement_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String)
    points = Column(Integer, default=10)

    unlocked_at = Column(DateTime, default=datetime.utcnow)
    achievement_metadata = Column(JSONB, default=dict)

    # Relaciones
    user = relationship("Profile", back_populates="achievements")

    __table_args__ = (
        {'schema': 'public'}
    )


class DailyStats(Base):
    __tablename__ = "daily_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    date = Column(Date, default=datetime.utcnow().date)

    # Tiempos de estudio
    study_time = Column(Interval)
    planned_study_time = Column(Interval)

    # Actividad
    tasks_completed = Column(Integer, default=0)
    flashcards_reviewed = Column(Integer, default=0)
    quizzes_taken = Column(Integer, default=0)

    # Rendimiento
    average_quiz_score = Column(Float)
    study_streak_days = Column(Integer, default=0)

    # Metadatos
    mood_rating = Column(Integer)
    productivity_rating = Column(Integer)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("Profile", back_populates="daily_stats")

    __table_args__ = (
        {'schema': 'public'}
    )