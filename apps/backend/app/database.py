from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .settings import settings

# URL de conexión a la base de datos
# Para desarrollo local, usar SQLite. Para producción, configurar DATABASE_URL con la URL de Supabase
DATABASE_URL = "sqlite:///./uni_ai.db"  # Forzar SQLite para desarrollo local

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para crear todas las tablas
def create_tables():
    Base.metadata.create_all(bind=engine)