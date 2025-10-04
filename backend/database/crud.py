from sqlmodel import Session, select

from backend.database.models import UserModel


def create_user(session: Session, user: UserModel) -> UserModel:
    session.add(user)
    session.commit()
    return session.exec(select(UserModel).where(UserModel.email == user.email)).first()
