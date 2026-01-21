# UniAI — Plataforma de organización + estudio con IA (Next.js + FastAPI + Supabase + Groq)

Monorepo con:
- `apps/web`: Frontend **Next.js** (para desplegar en **Vercel**)
- `apps/backend`: Backend **FastAPI** + jobs (Celery) (para desplegar en **Render** o **Railway**)

## Requisitos
- Node.js 18+ (recomendado 20)
- Python 3.11+
- Cuenta/proyecto en Supabase (DB/Auth/Storage)
- API key de Groq

## Estructura
- `apps/web/`: UI
- `apps/backend/`: API + worker

## Variables de entorno
Copia los ejemplos:
- `apps/web/env.example` → `apps/web/.env.local`
- `apps/backend/env.example` → `apps/backend/env`

> Nota: en este workspace `.env.example` puede estar bloqueado por configuración. Por eso usamos `env.example`.

## Dev (rápido)
### Frontend
```bash
cd apps/web
npm run dev
```

### Backend API
```bash
cd apps/backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Worker (opcional en dev)
Requiere Redis local o remoto:
```bash
cd apps/backend
celery -A app.worker.celery worker --loglevel=INFO
```

## Deploy (Render/Railway)
### Render (simple)
- **Web Service** apuntando a `apps/backend`
  - Build: `pip install -r requirements.txt`
  - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Worker Service** apuntando a `apps/backend`
  - Start: `celery -A app.worker.celery worker --loglevel=INFO`
- **Redis**: añade un Redis y copia `REDIS_URL`
- Variables: copia desde `apps/backend/env.example`

### Vercel (frontend)
- Proyecto apuntando a `apps/web`
- Variables: usa `apps/web/env.example` (en Vercel serán Environment Variables)

