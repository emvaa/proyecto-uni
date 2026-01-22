from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import CurrentUser, AuthUser
from ..schemas import (
    Task, TaskCreate, TaskUpdate, TaskAnalysisRequest, TaskAnalysisResponse
)
from ..models import Task as TaskModel
from ..services.ai_service import AIService

router = APIRouter(prefix="/tasks", tags=["tasks"])
ai_service = AIService()


@router.post("/", response_model=Task)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Crear una nueva tarea"""
    db_task = TaskModel(
        user_id=user.id,
        **task.model_dump()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/", response_model=List[Task])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    subject_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Obtener tareas del usuario con filtros opcionales"""
    query = db.query(TaskModel).filter(TaskModel.user_id == user.id)

    if status:
        query = query.filter(TaskModel.status == status)
    if priority:
        query = query.filter(TaskModel.priority == priority)
    if subject_id:
        query = query.filter(TaskModel.subject_id == subject_id)

    # Ordenar por prioridad y fecha límite
    query = query.order_by(
        desc(TaskModel.priority == "urgent"),
        desc(TaskModel.priority == "high"),
        desc(TaskModel.priority == "medium"),
        TaskModel.due_date.asc().nulls_last()
    )

    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Obtener una tarea específica"""
    task = db.query(TaskModel).filter(
        and_(TaskModel.id == task_id, TaskModel.user_id == user.id)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Actualizar una tarea"""
    task = db.query(TaskModel).filter(
        and_(TaskModel.id == task_id, TaskModel.user_id == user.id)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Actualizar campos proporcionados
    for field, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    # Marcar como completada si el status cambió a completed
    if task_update.status == "completed" and task.status != "completed":
        task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Eliminar una tarea"""
    task = db.query(TaskModel).filter(
        and_(TaskModel.id == task_id, TaskModel.user_id == user.id)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/analyze", response_model=TaskAnalysisResponse)
async def analyze_task(
    task_id: str,
    analysis_request: TaskAnalysisRequest,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Analizar una tarea con IA para generar explicación y solución"""
    task = db.query(TaskModel).filter(
        and_(TaskModel.id == task_id, TaskModel.user_id == user.id)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        # Analizar el contenido de la tarea con IA
        analysis_result = await ai_service.analyze_task_content(
            task.title,
            task.description or "",
            analysis_request.file_url,
            analysis_request.content_text
        )

        # Actualizar la tarea con el análisis de IA
        task.ai_analysis = analysis_result["analysis"]
        task.ai_explanation = analysis_result["explanation"]
        task.ai_solution = analysis_result["solution"]

        # Estimar dificultad basada en el análisis
        task.priority = ai_service.estimate_difficulty_priority(analysis_result["analysis"])

        db.commit()
        db.refresh(task)

        return TaskAnalysisResponse(**analysis_result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.get("/upcoming/deadlines")
async def get_upcoming_deadlines(
    days: int = 7,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Obtener tareas con fechas límite próximas"""
    cutoff_date = datetime.utcnow() + timedelta(days=days)

    tasks = db.query(TaskModel).filter(
        and_(
            TaskModel.user_id == user.id,
            TaskModel.due_date <= cutoff_date,
            TaskModel.status.in_(["pending", "in_progress"])
        )
    ).order_by(TaskModel.due_date.asc()).all()

    return {
        "upcoming_deadlines": [
            {
                "id": task.id,
                "title": task.title,
                "due_date": task.due_date,
                "priority": task.priority,
                "subject": task.subject.name if task.subject else None,
                "days_remaining": (task.due_date - datetime.utcnow()).days if task.due_date else None
            }
            for task in tasks
        ]
    }


@router.get("/stats/overview")
async def get_task_stats(
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Obtener estadísticas generales de tareas"""
    total_tasks = db.query(TaskModel).filter(TaskModel.user_id == user.id).count()
    completed_tasks = db.query(TaskModel).filter(
        and_(TaskModel.user_id == user.id, TaskModel.status == "completed")
    ).count()

    pending_tasks = db.query(TaskModel).filter(
        and_(TaskModel.user_id == user.id, TaskModel.status.in_(["pending", "in_progress"]))
    ).count()

    overdue_tasks = db.query(TaskModel).filter(
        and_(
            TaskModel.user_id == user.id,
            TaskModel.due_date < datetime.utcnow(),
            TaskModel.status.in_(["pending", "in_progress"])
        )
    ).count()

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }