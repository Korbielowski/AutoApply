from sqlmodel import Session, SQLModel, select

from backend.database.models import (
    CertificateModel,
    CharityModel,
    EducationModel,
    ExperienceModel,
    LanguageModel,
    LocationModel,
    ProgrammingLanguageModel,
    ProjectModel,
    SocialPlatformModel,
    ToolModel,
    UserModel,
    UserPreferencesModel,
    WebsiteModel,
)
from backend.logging import get_logger

logger = get_logger()


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


def get_user_preferences(
    session: Session, user: UserModel
) -> UserPreferencesModel | None:
    return session.exec(
        select(UserPreferencesModel).where(
            UserPreferencesModel.user_id == user.id
        )
    ).first()


def get_skills(session: Session, user: UserModel) -> dict:
    skills_dict = {
        "programming_languages": session.exec(
            select(ProgrammingLanguageModel).where(
                ProgrammingLanguageModel.user_id == user.id
            )
        ).all(),
        "languages": session.exec(
            select(LanguageModel).where(LanguageModel.user_id == user.id)
        ).all(),
        "tools": session.exec(
            select(ToolModel).where(ToolModel.user_id == user.id)
        ).all(),
        "certificates": session.exec(
            select(CertificateModel).where(CertificateModel.user_id == user.id)
        ).all(),
    }
    for key, val in skills_dict.items():
        for index, model in enumerate(val):
            model = model.model_dump()
            model.pop("id", None)
            model.pop("user_id", None)
            val[index] = model

    return skills_dict


def get_model(
    session: Session,
    user: UserModel,
    model: type[
        LocationModel,
        ProgrammingLanguageModel,
        LanguageModel,
        ToolModel,
        CertificateModel,
        CharityModel,
        EducationModel,
        ExperienceModel,
        ProjectModel,
        SocialPlatformModel,
        WebsiteModel,
    ],
    as_dict: bool = True,
) -> list:
    # TODO: Make this catch more errors
    if not issubclass(model, SQLModel):
        logger.error(
            f"Wrong model type given. Expected: SQLModel, given: {model.__class__.__name__}. Returning empty list"
        )
        return []

    model_list = session.exec(
        select(model).where(model.user_id == user.id)
    ).all()

    output = []
    for item in model_list:
        item = item.model_dump()
        item.pop("id", None)
        item.pop("user_id", None)
        output.append(item)

    return output
