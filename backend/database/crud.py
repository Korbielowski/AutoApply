from sqlmodel import Session

from backend.database.models import UserModel


def create_user(session: Session, user: UserModel) -> UserModel:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
