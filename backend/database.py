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
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

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
