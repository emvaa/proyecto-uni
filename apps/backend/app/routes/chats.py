from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..auth import CurrentUser, AuthUser
from ..schemas import ChatRequest, ChatResponse
from ..models import Chat as ChatModel, ChatMessage as ChatMessageModel, Task as TaskModel
from ..services.ai_service import AIService

router = APIRouter(prefix="/chats", tags=["chats"])
ai_service = AIService()


@router.get("/", response_model=List[dict])
async def get_user_chats(
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Obtener todos los chats del usuario"""
    chats = db.query(ChatModel).filter(ChatModel.user_id == user.id).order_by(desc(ChatModel.updated_at)).all()

    result = []
    for chat in chats:
        # Obtener último mensaje
        last_message = db.query(ChatMessageModel).filter(
            ChatMessageModel.chat_id == chat.id
        ).order_by(desc(ChatMessageModel.created_at)).first()

        result.append({
            "id": str(chat.id),
            "title": chat.title,
            "chat_type": chat.chat_type,
            "task_id": str(chat.task_id) if chat.task_id else None,
            "subject_id": str(chat.subject_id) if chat.subject_id else None,
            "is_active": chat.is_active,
            "last_message": last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else last_message.content if last_message else None,
            "last_message_at": last_message.created_at if last_message else None,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at
        })

    return result


@router.get("/{chat_id}/messages", response_model=List[dict])
async def get_chat_messages(
    chat_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Obtener mensajes de un chat específico"""
    # Verificar que el chat pertenece al usuario
    chat = db.query(ChatModel).filter(
        ChatModel.id == chat_id,
        ChatModel.user_id == user.id
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = db.query(ChatMessageModel).filter(
        ChatMessageModel.chat_id == chat_id
    ).order_by(ChatMessageModel.created_at).offset(skip).limit(limit).all()

    return [{
        "id": str(msg.id),
        "role": msg.role,
        "content": msg.content,
        "message_type": msg.message_type,
        "tokens_used": msg.tokens_used,
        "model_used": msg.model_used,
        "created_at": msg.created_at
    } for msg in messages]


@router.post("/{chat_id}/messages", response_model=dict)
async def send_chat_message(
    chat_id: str,
    message: ChatRequest,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Enviar un mensaje a un chat específico"""
    # Verificar que el chat pertenece al usuario
    chat = db.query(ChatModel).filter(
        ChatModel.id == chat_id,
        ChatModel.user_id == user.id
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Guardar mensaje del usuario
    user_message = ChatMessageModel(
        chat_id=chat_id,
        user_id=user.id,
        role="user",
        content=message.message
    )
    db.add(user_message)

    # Preparar contexto para IA
    context = ""
    if chat.chat_type == "task" and chat.task_id:
        # Obtener información de la tarea para contexto
        task = db.query(TaskModel).filter(TaskModel.id == chat.task_id).first()
        if task:
            context = f"""
            Información de la tarea:
            Título: {task.title}
            Descripción: {task.description or 'No disponible'}
            Materia: {task.subject.name if task.subject else 'No especificada'}
            Estado: {task.status}
            Análisis previo: {task.ai_analysis or 'No disponible'}
            """

    try:
        # Obtener respuesta de IA
        ai_response = await ai_service.generate_chat_response(
            user_message=message.message,
            chat_type=chat.chat_type,
            mode=message.mode,
            context=context
        )

        # Guardar respuesta de IA
        ai_message = ChatMessageModel(
            chat_id=chat_id,
            user_id=user.id,  # El sistema responde como el usuario (para simplificar)
            role="assistant",
            content=ai_response["content"],
            tokens_used=ai_response.get("tokens_used"),
            model_used=ai_response.get("model_used", "llama-3.1-8b-instant")
        )
        db.add(ai_message)

        # Actualizar timestamp del chat
        chat.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(ai_message)

        return {
            "id": str(ai_message.id),
            "role": ai_message.role,
            "content": ai_message.content,
            "message_type": ai_message.message_type,
            "tokens_used": ai_message.tokens_used,
            "model_used": ai_message.model_used,
            "created_at": ai_message.created_at
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating AI response: {str(e)}")


@router.get("/general")
async def get_general_chat(
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Obtener el chat general del usuario"""
    chat = db.query(ChatModel).filter(
        ChatModel.user_id == user.id,
        ChatModel.chat_type == "general"
    ).first()

    if not chat:
        # Crear chat general si no existe
        chat = ChatModel(
            user_id=user.id,
            title="Chat General",
            chat_type="general"
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)

    return {
        "id": str(chat.id),
        "title": chat.title,
        "chat_type": chat.chat_type,
        "created_at": chat.created_at
    }


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    db: Session = Depends(get_db),
    user: AuthUser = CurrentUser
):
    """Eliminar un chat (solo chats de tareas, no el general)"""
    chat = db.query(ChatModel).filter(
        ChatModel.id == chat_id,
        ChatModel.user_id == user.id
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat.chat_type == "general":
        raise HTTPException(status_code=400, detail="Cannot delete general chat")

    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted successfully"}