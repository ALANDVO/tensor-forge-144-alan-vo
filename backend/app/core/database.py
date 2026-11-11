"""Database session management and base model."""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event, Column, Integer, String, Text, Boolean, DateTime, func, JSON, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class PromptTemplate(Base):
    """Prompt template model for managing LLM prompt templates."""
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=False)
    model = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, nullable=True, default=list)
    category = Column(String(100), nullable=True, index=True)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    pool_pre_ping=True,
)

# Enable foreign keys for SQLite
if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database session outside FastAPI."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_default_prompts() -> None:
    """Seed database with default prompt templates."""
    db = SessionLocal()
    try:
        # Check if default "小码辉" prompt already exists
        existing = db.execute(
            select(PromptTemplate).where(
                PromptTemplate.name == "小码辉 Default",
                PromptTemplate.model.is_(None),
                PromptTemplate.is_default == True
            )
        ).scalar_one_or_none()
        
        if not existing:
            default_prompt = PromptTemplate(
                name="小码辉 Default",
                description="Default 小码辉 persona for general-purpose assistance",
                template="You are 小码辉, a helpful, harmless, and honest AI assistant. Provide accurate, concise, and safe responses to user queries.",
                model=None,  # Global default
                tags=["default", "persona", "小码辉"],
                category="general",
                is_default=True,
            )
            db.add(default_prompt)
            db.commit()
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables and seed default data."""
    Base.metadata.create_all(bind=engine)
    seed_default_prompts()
