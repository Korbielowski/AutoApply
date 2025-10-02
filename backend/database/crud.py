from sqlmodel import Session, select

from backend.database.models import User, UserModel


def create_user(session: Session, user: User) -> UserModel:
    session.add(user)
    session.commit()
    return session.exec(select(UserModel).where(UserModel.email == user.email)).first()
