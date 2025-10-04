from sqlmodel import SQLModel, create_engine

from backend.config import settings

engine = create_engine(str(settings.DATABASE_URI))


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
