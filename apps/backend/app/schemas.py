from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID


# =====================================================
# RESPUESTAS BÁSICAS
# =====================================================

class HealthResponse(BaseModel):
    status: str = "ok"


class SignedUploadRequest(BaseModel):
    bucket: str = Field(default="files")
    path: str = Field(..., description="Storage path, e.g. userId/tasks/taskId/file.pdf")
    content_type: str | None = None


class SignedUploadResponse(BaseModel):
    bucket: str
    path: str
    signed_url: str
    token: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    mode: str = Field(default="learn", description="learn | review")
    task_id: str | None = None


class ChatResponse(BaseModel):
    answer: str


# =====================================================
# USUARIOS Y PERFILES
# =====================================================

class ProfileBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    study_preferences: Optional[Dict[str, Any]] = None
    academic_info: Optional[Dict[str, Any]] = None


class Profile(ProfileBase):
    id: UUID
    study_preferences: Dict[str, Any]
    academic_info: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# MATERIAS
# =====================================================

class SubjectBase(BaseModel):
    name: str
    code: Optional[str] = None
    color: str = "#3b82f6"
    description: Optional[str] = None
    professor: Optional[str] = None
    credits: int = 3
    difficulty_level: int = Field(3, ge=1, le=5)


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    professor: Optional[str] = None
    credits: Optional[int] = None
    difficulty_level: Optional[int] = None
    schedule: Optional[Dict[str, Any]] = None


class Subject(SubjectBase):
    id: UUID
    user_id: UUID
    schedule: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# TAREAS
# =====================================================

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str = Field("homework", pattern="^(homework|exam|project|reading|practice|other)$")
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")


class TaskCreate(TaskBase):
    subject_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    estimated_duration: Optional[str] = None  # Interval as string
    tags: List[str] = []


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    subject_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    estimated_duration: Optional[str] = None
    actual_duration: Optional[str] = None
    tags: Optional[List[str]] = None
    progress_percentage: Optional[int] = None
    notes: Optional[str] = None


class Task(TaskBase):
    id: UUID
    user_id: UUID
    subject_id: Optional[UUID] = None
    status: str = "pending"
    due_date: Optional[datetime] = None
    estimated_duration: Optional[str] = None
    actual_duration: Optional[str] = None
    completed_at: Optional[datetime] = None
    attachments: List[Dict[str, Any]] = []
    ai_analysis: Dict[str, Any] = {}
    ai_explanation: Dict[str, Any] = {}
    ai_solution: Dict[str, Any] = {}
    tags: List[str] = []
    progress_percentage: int = 0
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# FLASHCARDS
# =====================================================

class FlashcardBase(BaseModel):
    front_content: str
    back_content: str
    card_type: str = "basic"


class FlashcardCreate(FlashcardBase):
    subject_id: UUID
    difficulty_level: int = Field(3, ge=1, le=5)
    tags: List[str] = []
    source_material: Optional[str] = None


class FlashcardUpdate(BaseModel):
    front_content: Optional[str] = None
    back_content: Optional[str] = None
    card_type: Optional[str] = None
    difficulty_level: Optional[int] = None
    tags: Optional[List[str]] = None


class Flashcard(FlashcardBase):
    id: UUID
    user_id: UUID
    subject_id: UUID
    difficulty_level: int = 3
    tags: List[str] = []
    source_task_id: Optional[UUID] = None
    source_material: Optional[str] = None
    easiness_factor: float = 2.5
    interval_days: int = 1
    repetitions: int = 0
    next_review_date: date
    times_reviewed: int = 0
    times_correct: int = 0
    times_incorrect: int = 0
    last_reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# QUIZZES
# =====================================================

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    quiz_type: str = "practice"


class QuizCreate(QuizBase):
    subject_id: UUID
    task_id: Optional[UUID] = None
    total_questions: int = 10
    time_limit: Optional[str] = None
    passing_score: Optional[float] = None


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    total_questions: Optional[int] = None
    time_limit: Optional[str] = None
    passing_score: Optional[float] = None


class Quiz(QuizBase):
    id: UUID
    user_id: UUID
    subject_id: UUID
    task_id: Optional[UUID] = None
    total_questions: int = 10
    time_limit: Optional[str] = None
    passing_score: Optional[float] = None
    questions: List[Dict[str, Any]] = []
    generated_by_ai: bool = True
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    time_taken: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# CALENDARIO
# =====================================================

class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: str = "other"


class CalendarEventCreate(CalendarEventBase):
    start_date: datetime
    end_date: Optional[datetime] = None
    is_all_day: bool = False
    subject_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    study_session_id: Optional[UUID] = None
    priority: str = "medium"
    color: str = "#3b82f6"


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_all_day: Optional[bool] = None
    event_type: Optional[str] = None
    subject_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    study_session_id: Optional[UUID] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    color: Optional[str] = None
    reminder_settings: Optional[Dict[str, Any]] = None


class CalendarEvent(CalendarEventBase):
    id: UUID
    user_id: UUID
    start_date: datetime
    end_date: Optional[datetime] = None
    is_all_day: bool = False
    recurrence_rule: Optional[Dict[str, Any]] = None
    subject_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    study_session_id: Optional[UUID] = None
    reminder_settings: Dict[str, Any] = {}
    priority: str = "medium"
    status: str = "scheduled"
    color: str = "#3b82f6"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# ESTADÍSTICAS Y LOGROS
# =====================================================

class Achievement(BaseModel):
    id: UUID
    user_id: UUID
    achievement_type: str
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    points: int = 10
    unlocked_at: datetime
    achievement_metadata: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class DailyStats(BaseModel):
    id: UUID
    user_id: UUID
    date: date
    study_time: Optional[str] = None
    planned_study_time: Optional[str] = None
    tasks_completed: int = 0
    flashcards_reviewed: int = 0
    quizzes_taken: int = 0
    average_quiz_score: Optional[float] = None
    study_streak_days: int = 0
    mood_rating: Optional[int] = None
    productivity_rating: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# SESIONES DE ESTUDIO
# =====================================================

class StudySessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    session_type: str = "practice"


class StudySessionCreate(StudySessionBase):
    subject_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    planned_duration: Optional[str] = None
    topics_covered: List[str] = []


class StudySessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    end_time: Optional[datetime] = None
    actual_duration: Optional[str] = None
    topics_covered: Optional[List[str]] = None
    difficulty_rating: Optional[int] = None
    notes: Optional[str] = None
    what_learned: Optional[str] = None
    what_to_improve: Optional[str] = None


class StudySession(StudySessionBase):
    id: UUID
    user_id: UUID
    subject_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    planned_duration: Optional[str] = None
    actual_duration: Optional[str] = None
    topics_covered: List[str] = []
    difficulty_rating: Optional[int] = None
    flashcards_reviewed: int = 0
    questions_answered: int = 0
    correct_answers: int = 0
    notes: Optional[str] = None
    what_learned: Optional[str] = None
    what_to_improve: Optional[str] = None
    ai_insights: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# ANÁLISIS Y REPORTES
# =====================================================

class TaskAnalysisRequest(BaseModel):
    task_id: UUID
    file_url: Optional[str] = None
    content_text: Optional[str] = None


class TaskAnalysisResponse(BaseModel):
    analysis: Dict[str, Any]
    explanation: Dict[str, Any]
    solution: Dict[str, Any]
    estimated_difficulty: int
    suggested_approach: str
    key_concepts: List[str]


class StudyRecommendation(BaseModel):
    recommended_sessions: List[Dict[str, Any]]
    priority_subjects: List[Dict[str, Any]]
    study_plan: Dict[str, Any]
    estimated_completion_time: str
    motivation_tips: List[str]


class PerformanceAnalytics(BaseModel):
    total_study_time: str
    average_daily_study: str
    completion_rate: float
    strongest_subjects: List[Dict[str, Any]]
    weakest_subjects: List[Dict[str, Any]]
    study_streak: int
    achievements_unlocked: int
    predicted_gpa: Optional[float] = None

