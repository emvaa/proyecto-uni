from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..auth import CurrentUser, AuthUser
from ..schemas import (
    Subject, SubjectCreate, SubjectUpdate
)
from ..models import Subject as SubjectModel, Task as TaskModel

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.post("/", response_model=Subject)
async def create_subject(
    subject: SubjectCreate,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Crear una nueva materia"""
    db_subject = SubjectModel(
        user_id=user.id,
        **subject.model_dump()
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


@router.get("/", response_model=List[Subject])
async def get_subjects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Obtener materias del usuario"""
    subjects = db.query(SubjectModel).filter(SubjectModel.user_id == user.id).offset(skip).limit(limit).all()
    return subjects


@router.get("/{subject_id}", response_model=Subject)
async def get_subject(
    subject_id: str,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Obtener una materia específica"""
    subject = db.query(SubjectModel).filter(
        SubjectModel.id == subject_id,
        SubjectModel.user_id == user.id
    ).first()

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    return subject


@router.put("/{subject_id}", response_model=Subject)
async def update_subject(
    subject_id: str,
    subject_update: SubjectUpdate,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Actualizar una materia"""
    subject = db.query(SubjectModel).filter(
        SubjectModel.id == subject_id,
        SubjectModel.user_id == user.id
    ).first()

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Actualizar campos proporcionados
    for field, value in subject_update.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)

    db.commit()
    db.refresh(subject)
    return subject


@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: str,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Eliminar una materia"""
    subject = db.query(SubjectModel).filter(
        SubjectModel.id == subject_id,
        SubjectModel.user_id == user.id
    ).first()

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Verificar que no haya tareas asociadas
    tasks_count = db.query(TaskModel).filter(TaskModel.subject_id == subject_id).count()
    if tasks_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete subject with associated tasks")

    db.delete(subject)
    db.commit()
    return {"message": "Subject deleted successfully"}


@router.get("/{subject_id}/stats")
async def get_subject_stats(
    subject_id: str,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Obtener estadísticas de una materia"""
    subject = db.query(SubjectModel).filter(
        SubjectModel.id == subject_id,
        SubjectModel.user_id == user.id
    ).first()

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Estadísticas básicas
    total_tasks = db.query(TaskModel).filter(TaskModel.subject_id == subject_id).count()
    completed_tasks = db.query(TaskModel).filter(
        TaskModel.subject_id == subject_id,
        TaskModel.status == "completed"
    ).count()

    pending_tasks = db.query(TaskModel).filter(
        TaskModel.subject_id == subject_id,
        TaskModel.status.in_(["pending", "in_progress"])
    ).count()

    return {
        "subject_id": subject_id,
        "subject_name": subject.name,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }