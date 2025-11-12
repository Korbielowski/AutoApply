from sqlmodel import Session, select

from backend.database.models import UserModel


def create_user(session: Session, user: UserModel) -> UserModel:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, email: str) -> None:
    session.delete(
        session.exec(select(UserModel).where(UserModel.email == email)).first()
    )
    session.commit()
