from typing import Annotated, Generator

from fastapi import Depends
from sqlmodel import Session, func, select

from backend.database.db import engine
from backend.database.models import UserModel

user: UserModel | None = None


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def current_user() -> UserModel | None:
    if user:
        return user

    with Session(engine) as session:
        profile_count = session.scalar(func.count(UserModel.id))
        if profile_count > 1:
            return None
        return session.exec(select(UserModel)).first()


def set_current_user(session: Session, email: str) -> None:
    global user
    user = session.exec(select(UserModel).where(UserModel.email == email)).first()


SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[UserModel, Depends(current_user)]
