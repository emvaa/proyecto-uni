from groq import Groq
from fastapi import APIRouter, HTTPException

from ..auth import CurrentUser, AuthUser
from ..schemas import ChatRequest, ChatResponse
from ..settings import settings

router = APIRouter(tags=["chat"])


def _system_prompt(mode: str) -> str:
    mode = (mode or "learn").lower()
    if mode not in {"learn", "review"}:
        mode = "learn"

    if mode == "review":
        return (
            "Eres un tutor universitario. Estás en MODO REPASO.\n"
            "- Sé conciso.\n"
            "- Resume primero y luego haz 3-5 preguntas rápidas.\n"
            "- Si falta información, pregunta antes de asumir.\n"
        )

    return (
        "Eres un tutor universitario. Estás en MODO APRENDER.\n"
        "- No des la solución completa si el estudiante no mostró intento.\n"
        "- Da pistas graduadas y guía paso a paso.\n"
        "- Explica el razonamiento, y pide al estudiante que complete el siguiente paso.\n"
        "- Si falta información, pregunta antes de asumir.\n"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, user: AuthUser = CurrentUser) -> ChatResponse:
    # MVP: sin RAG aún (luego: recuperar chunks por task_id y añadir citas)
    if not settings.groq_api_key:
        raise HTTPException(status_code=500, detail="Server misconfigured: GROQ_API_KEY is missing")
    try:
        client = Groq(api_key=settings.groq_api_key)
        completion = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": _system_prompt(body.mode)},
                {
                    "role": "user",
                    "content": f"Usuario: {user.id}\n\nMensaje:\n{body.message}",
                },
            ],
            temperature=0.3,
        )
        answer = completion.choices[0].message.content or ""
        return ChatResponse(answer=answer.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq error: {e}")

