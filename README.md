# 🎓 UniAI - Asistente Universitario con IA

Una plataforma completa para estudiantes universitarios que combina gestión académica inteligente, tutoría con IA, y herramientas de estudio avanzadas.

## ✨ Características Principales

### 🤖 **Tutor Universitario con IA**
- Chat inteligente con Groq AI (Llama-3.1-8B)
- Modos "Aprender" y "Repasar" adaptativos
- Análisis automático de tareas y explicaciones paso a paso
- Chats separados por tarea para contextualización

### 📚 **Gestión Académica Completa**
- **Materias**: Registro y organización por asignaturas con fechas de exámenes
- **Tareas**: Subida de archivos, análisis con IA, seguimiento de progreso
- **Calendario**: Eventos académicos y recordatorios inteligentes
- **Prioridades**: Sistema automático de urgencia y dificultad

### 🎯 **Sistema de Estudio Inteligente**
- **Flashcards** con repaso espaciado (Spaced Repetition)
- **Quizzes generados por IA** adaptados a tu nivel
- **Análisis de rendimiento** con métricas detalladas
- **Recomendaciones personalizadas** basadas en tu progreso

### 🏆 **Gamificación y Motivación**
- **Sistema de logros** desbloqueables
- **Puntos y recompensas** por consistencia
- **Estadísticas de progreso** motivacionales
- **Rachas de estudio** y records personales

## 🚀 **Inicio Rápido**

### 1. **Configurar Supabase**

1. Ve a [Supabase](https://supabase.com) y crea un proyecto
2. Ve a **SQL Editor** y ejecuta el contenido del archivo `database_schema.sql`
3. Ve a **Settings > API** y copia:
   - Project URL
   - Anon Public Key
   - Service Role Key
   - JWKS URL
4. Ve a **Settings > Database** y copia la Connection String

### 2. **Configurar Variables de Entorno**

**Backend (apps/backend/env):**
```bash
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_anon_key
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key
SUPABASE_JWKS_URL=https://tu-proyecto.supabase.co/auth/v1/jwks

# Database (Connection string de Supabase)
DATABASE_URL=postgresql://postgres.[password]@aws-0-[region].pooler.supabase.com:5432/postgres

# Groq AI
GROQ_API_KEY=gsk_tu_api_key_de_groq
GROQ_MODEL=llama-3.1-8b-instant

# App settings
APP_ENV=dev
APP_ORIGIN=http://localhost:3000
```

**Frontend (apps/web/.env.local):**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://tu-proyecto.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=tu_anon_key
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. **Instalar Dependencias**

```bash
# Backend
cd apps/backend
pip install -r requirements.txt

# Frontend
cd apps/web
npm install
```

### 4. **Ejecutar la Aplicación**

```bash
# Terminal 1 - Backend
cd apps/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd apps/web
npm run dev
```

### 5. **Acceder**

- **Aplicación**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 **Primeros Pasos en la App**

1. **Regístrate** con tu email
2. **Verifica tu email** (revisa tu bandeja de entrada)
3. **Inicia sesión**
4. **Agrega tus materias** (pestaña "Materias")
5. **Crea tu primera tarea** (pestaña "Tareas")
6. **Chatea con la IA** sobre tus estudios

## 🏗️ **Arquitectura Técnica**

### **Stack Tecnológico**
- **Frontend**: Next.js 16 + TypeScript + Tailwind CSS + React Context
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + JWT
- **Base de Datos**: Supabase (PostgreSQL + Auth + Storage + RLS)
- **IA**: Groq API (Llama-3.1-8B) - GRATUITO
- **Autenticación**: Supabase Auth con tokens JWT

### **Estructura del Proyecto**
```
uni/
├── apps/
│   ├── backend/           # API FastAPI
│   │   ├── app/
│   │   │   ├── routes/    # Endpoints REST
│   │   │   │   ├── tasks.py
│   │   │   │   ├── subjects.py
│   │   │   │   ├── chats.py
│   │   │   │   └── chat.py (legacy)
│   │   │   ├── models.py  # Modelos SQLAlchemy
│   │   │   ├── schemas.py # Pydantic schemas
│   │   │   └── services/  # Servicios de IA
│   │   └── env            # Variables de entorno
│   └── web/               # Frontend Next.js
│       ├── src/
│       │   ├── app/       # App Router + páginas
│       │   ├── components/# Componentes React
│       │   ├── contexts/  # AuthContext
│       │   └── lib/       # Supabase client
│       └── .env.local     # Variables de entorno
├── database_schema.sql    # Schema completo de BD
└── README.md
```

## 🔧 **APIs Disponibles**

### **Materias**
- `GET /subjects` - Listar materias del usuario
- `POST /subjects` - Crear nueva materia
- `PUT /subjects/{id}` - Actualizar materia
- `DELETE /subjects/{id}` - Eliminar materia
- `GET /subjects/{id}/stats` - Estadísticas de materia

### **Tareas**
- `GET /tasks` - Listar tareas con filtros (status, priority, subject)
- `POST /tasks` - Crear nueva tarea
- `PUT /tasks/{id}` - Actualizar tarea
- `DELETE /tasks/{id}` - Eliminar tarea
- `POST /tasks/{id}/analyze` - Analizar tarea con IA
- `GET /tasks/upcoming/deadlines` - Próximas fechas límite
- `GET /tasks/stats/overview` - Estadísticas generales

### **Chats**
- `GET /chats` - Listar chats del usuario
- `GET /chats/general` - Obtener chat general
- `GET /chats/{id}/messages` - Obtener mensajes de un chat
- `POST /chats/{id}/messages` - Enviar mensaje a un chat
- `DELETE /chats/{id}` - Eliminar chat

### **Sistema de Estudio**
- Rutas pendientes de implementación para flashcards y quizzes

## 🎯 **Flujo de Trabajo Típico**

1. **Configuración Inicial**
   - Registrar materias del semestre
   - Configurar preferencias de estudio

2. **Gestión de Tareas**
   - Subir tarea (PDF/imagen) - IA analiza automáticamente
   - Chat específico por tarea para resolver dudas
   - Seguimiento de progreso y completación

3. **Estudio Diario**
   - Repasar flashcards (repaso espaciado)
   - Tomar quizzes generados por IA
   - Recibir recomendaciones personalizadas

4. **Chat General**
   - Consultas generales sobre estudios
   - Consejos de organización
   - Motivación y técnicas de estudio

## 🔐 **Seguridad**

- **Autenticación JWT** con Supabase
- **Row Level Security (RLS)** en todas las tablas
- **Validación automática de tokens**
- **Encriptación** de datos sensibles
- **Políticas de acceso** granular

## 📊 **Base de Datos**

### **Tablas Principales**
- `profiles` - Perfiles de usuario
- `subjects` - Materias/Asignaturas
- `tasks` - Tareas y actividades
- `chats` - Conversaciones (general o por tarea)
- `chat_messages` - Mensajes de chat
- `flashcards` - Sistema de tarjetas de estudio
- `quizzes` - Evaluaciones generadas por IA
- `calendar_events` - Eventos del calendario
- `achievements` - Logros desbloqueables
- `daily_stats` - Estadísticas diarias

### **Características**
- **Triggers automáticos** para actualizar timestamps
- **Índices optimizados** para búsquedas rápidas
- **Constraints y validaciones** en BD
- **Funciones helper** para operaciones comunes

## 🚀 **Despliegue en Producción**

### **Backend (Railway/Render)**
```bash
# Variables de entorno
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_JWKS_URL=...
GROQ_API_KEY=...
DATABASE_URL=...
APP_ENV=production
APP_ORIGIN=https://tu-frontend.vercel.app
```

### **Frontend (Vercel)**
```bash
# Variables de entorno
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_API_BASE_URL=https://tu-api.railway.app
```

## 🧪 **Testing**

```bash
# Backend
cd apps/backend
pytest  # (si implementas tests)

# Frontend
cd apps/web
npm run test
npm run build  # Verificar que compile correctamente
```

## 🤝 **Contribuir**

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 **Roadmap**

### **Próximas Funcionalidades**
- [ ] Sistema completo de flashcards con repaso espaciado
- [ ] Generador automático de quizzes por IA
- [ ] Calendario académico integrado
- [ ] Sistema de recordatorios push
- [ ] Análisis predictivo de calificaciones
- [ ] Modo colaborativo para grupos de estudio
- [ ] Integración con Moodle/Canvas
- [ ] App móvil React Native

### **Mejoras Técnicas**
- [ ] Tests automatizados completos
- [ ] CI/CD pipeline
- [ ] Monitoreo y logging avanzado
- [ ] Caché Redis para optimización
- [ ] API rate limiting
- [ ] Backup automático de BD

## 📞 **Soporte**

Si encuentras problemas:

1. **Revisa los logs** del backend y navegador
2. **Verifica las variables de entorno** están configuradas
3. **Confirma que la BD** está creada y accesible
4. **Revisa la documentación** de Supabase y Groq

### **Comandos Útiles**
```bash
# Ver logs del backend
tail -f logs/backend.log

# Verificar BD
psql $DATABASE_URL -c "SELECT * FROM profiles LIMIT 5;"

# Health checks
curl http://localhost:8000/health
curl http://localhost:3000/api/health
```

## 📋 **Licencia**

Este proyecto está bajo la **Licencia MIT**.

## 🙏 **Agradecimientos**

- **Supabase** por la increíble plataforma de BD y Auth
- **Groq** por el acceso gratuito a modelos de IA avanzados
- **Next.js** y **FastAPI** por los excelentes frameworks
- **Tailwind CSS** por el sistema de diseño utilitario

---

## 🎓 **¿Por qué UniAI?**

**UniAI no es solo una app de tareas.** Es tu **compañero de estudio inteligente** que:

- **Comprende** tus tareas y te explica conceptos complejos
- **Te motiva** con logros y seguimiento de progreso
- **Se adapta** a tu ritmo y estilo de aprendizaje
- **Te ayuda** a ser más eficiente y efectivo en tus estudios

**Construido con ❤️ para estudiantes universitarios de todo el mundo**

**¡Únete a la revolución del estudio inteligente! 🚀📚✨**

