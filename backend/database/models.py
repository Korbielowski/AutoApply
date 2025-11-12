import datetime
from enum import StrEnum
from typing import Callable

from pydantic import EmailStr
from sqlmodel import JSON, Column, Field, SQLModel

# TODO: Add model for storing all of the users preferences regarding scraping, cv creation and applying

# TODO: Add priority to each category of skills and qualifications, so that the system can decide what should go into cv


# TODO: How to recognise duplicate job offers on a different sites and on the same site at different time
# Maybe try using normalization of several job information e.g. title, company name and part of description and fuzzy matching
# https://github.com/rapidfuzz/RapidFuzz
class JobEntryModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    title: str
    company_name: str
    discovery_date: datetime.date = Field(default_factory=datetime.date.today)
    job_url: str
    requirements: str
    duties: str
    about_project: str
    offer_benefits: str
    location: str
    contract_type: str
    employment_type: str
    work_arrangement: str
    additional_information: None | str
    company_url: (
        None | str
    )  # TODO: Here LLM will need to find information on the internet


class JobEntry(SQLModel):
    title: str
    company_name: str
    discovery_date: datetime.date
    job_url: str
    requirements: str
    duties: str
    about_project: str
    offer_benefits: str
    location: str
    contract_type: str
    employment_type: str
    work_arrangement: str
    additional_information: None | str
    company_url: None | str


class AttributeType(StrEnum):
    id = "id"
    text = "text"
    aria_label = "aria_label"
    name = "name"
    element_type = "element_type"
    class_l = "class_l"


class Step(SQLModel):
    action: Callable
    html_element_attribute: str  # TODO: Experiment with Locators too if you can
    attribute_type: AttributeType
    arguments: dict


class AutomationSteps(SQLModel):
    login_to_page: list[Step]
    is_on_login_page: list[Step]
    navigate_to_login_page: list[Step]
    pass_cookies_popup: list[Step]
    navigate_to_job_list: list[Step]
    get_job_entries: list[Step]
    navigate_to_next_page: list[Step]
    # TODO: Uncomment if this function gets html elements get_job_information: list[Step]


class UserModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, max_length=255)
    first_name: str
    middle_name: str
    surname: str
    age: str | None


class User(SQLModel):
    email: EmailStr
    first_name: str
    middle_name: str
    surname: str
    age: str | None


class WebsiteModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    cookies: str
    user_email: EmailStr
    user_password: str
    url: str
    automation_steps: AutomationSteps | None = Field(
        sa_column=Column(JSON), default_factory=dict
    )


class Website(SQLModel):
    cookies: str
    user_email: EmailStr
    user_password: str
    url: str
    automation_steps: AutomationSteps | None


class LocationModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    country: str
    state: str
    city: str
    zip_code: str


class Location(SQLModel):
    country: str
    state: str
    city: str
    zip_code: str


class ProgrammingLanguageModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    language: str
    level: str  # Maybe in the future change to int


class ProgrammingLanguage(SQLModel):
    language: str
    level: str  # Maybe in the future change to int


class LanguageModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    language: str
    level: str  # Maybe in the future change to int


class Language(SQLModel):
    language: str
    level: str  # Maybe in the future change to int


class ToolModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    name: str
    level: str  # Maybe in the future change to int


class Tool(SQLModel):
    name: str
    level: str  # Maybe in the future change to int


class CertificateModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    name: str
    description: str
    organisation: str


class Certificate(SQLModel):
    name: str
    description: str
    organisation: str


class CharityModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    name: str
    description: str
    organisation: str
    start_date: datetime.date | None = Field(default=None)
    end_date: datetime.date | None = Field(default=None)


class Charity(SQLModel):
    name: str
    description: str
    organisation: str
    start_date: datetime.date | None
    end_date: datetime.date | None


class EducationModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    school: str
    major: str
    description: str
    start_date: datetime.date | None = Field(default=None)
    end_date: datetime.date | None = Field(default=None)


class Education(SQLModel):
    school: str
    major: str
    description: str
    start_date: datetime.date | None
    end_date: datetime.date | None


class ExperienceModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    company: str
    position: str
    description: str
    start_date: datetime.date | None = Field(default=None)
    end_date: datetime.date | None = Field(default=None)


class Experience(SQLModel):
    company: str
    position: str
    description: str
    start_date: datetime.date | None
    end_date: datetime.date | None


class ProjectModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    name: str
    description: str
    url: str


class Project(SQLModel):
    name: str
    description: str
    url: str


class SocialPlatformModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    name: str
    url: str


class SocialPlatform(SQLModel):
    name: str
    url: str


class ProfileInfo(SQLModel):
    profile: User
    locations: list[Location] | None
    programming_languages: list[ProgrammingLanguage] | None
    languages: list[Language] | None
    tools: list[Tool] | None
    certificates: list[Certificate] | None
    charities: list[Charity] | None
    educations: list[Education] | None
    experiences: list[Experience] | None
    projects: list[Project] | None
    social_platforms: list[SocialPlatform] | None
    websites: list[Website] | None


# locations: list[LocationModel] | None  # TODO: In the future make this priority list
