from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from .config import DATABASE_FILE

DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def init_db():
    from .models import (
        Paper, Summary, Comparison, Citation, ChatHistory,
        FinalReport, CoordinatorRun,
    )

    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:
        raise RuntimeError("Unable to initialize database") from exc
