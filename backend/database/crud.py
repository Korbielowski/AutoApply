from typing import Union

from sqlmodel import Session, SQLModel, select

from backend.database.models import (
    CandidateData,
    CertificateModel,
    CharityModel,
    EducationModel,
    ExperienceModel,
    JobEntry,
    JobEntryModel,
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
from backend.logger import get_logger

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
) -> list[
    Union[
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
    ]
]:
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


def get_candidate_data(session: Session, user: UserModel) -> CandidateData:
    locations = get_model(session=session, user=user, model=LocationModel)
    programming_languages = get_model(
        session=session, user=user, model=ProgrammingLanguageModel
    )
    languages = get_model(session=session, user=user, model=LanguageModel)
    tools = get_model(session=session, user=user, model=ToolModel)
    certificates = get_model(session=session, user=user, model=CertificateModel)
    experiences = get_model(session=session, user=user, model=ExperienceModel)
    charities = get_model(session=session, user=user, model=CharityModel)
    educations = get_model(session=session, user=user, model=EducationModel)
    social_platforms = get_model(
        session=session, user=user, model=SocialPlatformModel
    )
    full_name = (
        f"{user.first_name} {user.middle_name} {user.surname}"
        if user.middle_name
        else f"{user.first_name} {user.surname}"
    )
    projects = get_model(session=session, user=user, model=ProjectModel)
    return CandidateData(
        full_name=full_name,
        email=user.email,
        phone_number=user.phone_number,
        locations=locations,
        programming_languages=programming_languages,
        languages=languages,
        tools=tools,
        certificates=certificates,
        charities=charities,
        educations=educations,
        experiences=experiences,
        projects=projects,
        social_platforms=social_platforms,
    )


def get_job_entries(session: Session, user: UserModel):
    return session.exec(
        select(JobEntryModel).where(JobEntryModel.user_id == user.id)
    ).all()


def save_job_entry(
    session: Session, user: UserModel, job_entry: JobEntry
) -> None:
    job_entry_model = JobEntryModel.model_validate(job_entry.model_dump())
    job_entry_model.user_id = user.id
    session.add(job_entry_model)
    session.commit()
