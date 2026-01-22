from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings
from .database import create_tables
from .routes.health import router as health_router
from .routes.storage import router as storage_router
from .routes.chat import router as chat_router
from .routes.tasks import router as tasks_router
from .routes.subjects import router as subjects_router
from .routes.chats import router as chats_router


app = FastAPI(title="UniAI Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(storage_router)
app.include_router(chat_router)
app.include_router(tasks_router)
app.include_router(subjects_router)
app.include_router(chats_router)

# Crear tablas en la base de datos al iniciar
@app.on_event("startup")
async def startup_event():
    create_tables()

