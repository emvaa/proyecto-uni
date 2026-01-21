from celery import Celery

from .settings import settings


celery = Celery(
    "uniai",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


@celery.task(name="ingest_file")
def ingest_file(file_id: str) -> dict:
    """
    MVP placeholder.
    Later: download from Supabase Storage, extract text/OCR, chunk, embed, store in pgvector.
    """
    return {"file_id": file_id, "status": "todo"}

