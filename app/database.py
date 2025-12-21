from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from app.config import settings

# Crear engine de SQLAlchemy para SQL Server con pyodbc
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,                    # Número de conexiones en el pool
    max_overflow=10,                # Conexiones adicionales permitidas
    pool_pre_ping=True,             # Verificar conexiones antes de usar
    pool_recycle=3600,              # Reciclar conexiones cada hora
    echo=settings.DEBUG,            # Log de queries SQL en modo debug
    connect_args={
        "timeout": 30,              # Timeout de conexión
    }
)

# Crear SessionLocal con sessionmaker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base declarativa para modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener sesión de base de datos.
    Usar como generador para FastAPI dependencies.

    Ejemplo:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_connection():
    """Verificar conexión a la base de datos"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {str(e)}")
        return False
