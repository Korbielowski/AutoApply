from sqlmodel import Field, SQLModel

# from pydantic import Da

class JobEntry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    posting_id: int


class Profile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    fristname: str
    middlename: str
    surname: str
    age: int


class ProfileModel(SQLModel):
    firstname: str
    middlename: str
    surname: str
    age: str


class Location(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    country: str
    state: str
    city: str
    zipcode: str


class LocationModel(SQLModel):
    country: str
    state: str
    city: str
    zipcode: str


class ProgrammingLanguage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    language: str
    level: str  # Maybe in the future change to int


class ProgrammingLanguageModel(SQLModel):
    language: str
    level: str  # Maybe in the future change to int


class Language(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    language: str
    level: str  # Maybe in the future change to int


class LanguageModel(SQLModel):
    language: str
    level: str  # Maybe in the future change to int


class Tool(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    name: str
    level: str  # Maybe in the future change to int


class ToolModel(SQLModel):
    name: str
    level: str  # Maybe in the future change to int


class Certificate(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    name: str
    description: str
    organisation: str


class CertificateModel(SQLModel):
    name: str
    description: str
    organisation: str


class Charity(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    name: str
    description: str
    organisation: str
    # start_date: DateTime = Field(
    #     sa_column=Column(
    #         TIMESTAMP(timezone=True),
    #         nullable=False,
    #         server_default=text("CURRENT_TIMESTAMP"),
    #         server_onupdate=text("CURRENT_TIMESTAMP"),
    #     )
    # )
    # end_date: DateTime = Field(
    #     sa_column=Column(
    #         TIMESTAMP(timezone=True),
    #         nullable=False,
    #         server_default=text("CURRENT_TIMESTAMP"),
    #         server_onupdate=text("CURRENT_TIMESTAMP"),
    #     )
    # )


class CharityModel(SQLModel):
    name: str
    description: str
    organisation: str
    # start_date: DateTime
    # end_date: DateTime


class Education(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    school: str
    major: str
    description: str
    # start_date: DateTime = Field(
    #     sa_column=Column(
    #         TIMESTAMP(timezone=True),
    #         nullable=False,
    #         server_default=text("CURRENT_TIMESTAMP"),
    #         server_onupdate=text("CURRENT_TIMESTAMP"),
    #     )
    # )
    # end_date: DateTime = Field(
    #     sa_column=Column(
    #         TIMESTAMP(timezone=True),
    #         nullable=False,
    #         server_default=text("CURRENT_TIMESTAMP"),
    #         server_onupdate=text("CURRENT_TIMESTAMP"),
    #     )
    # )


class EducationModel(SQLModel):
    school: str
    major: str
    description: str
    # start_date: DateTime = Field(
    #     sa_column=Column(
    #         TIMESTAMP(timezone=True),
    #         nullable=False,
    #         server_default=text("CURRENT_TIMESTAMP"),
    #         server_onupdate=text("CURRENT_TIMESTAMP"),
    #     )
    # )
    # end_date: DateTime = Field(
    #     sa_column=Column(
    #         TIMESTAMP(timezone=True),
    #         nullable=False,
    #         server_default=text("CURRENT_TIMESTAMP"),
    #         server_onupdate=text("CURRENT_TIMESTAMP"),
    #     )
    # )


class Experience(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    company: str
    position: str
    description: str
    # start_date: DateTime = Field(
    #     sa_column=Column(
    #         TIMESTAMP(timezone=True),
    #         nullable=False,
    #         server_default=text("CURRENT_TIMESTAMP"),
    #         server_onupdate=text("CURRENT_TIMESTAMP"),
    #     )
    # )
    # end_date: DateTime = Field(
    #     sa_column=Column(
    #         TIMESTAMP(timezone=True),
    #         nullable=False,
    #         server_default=text("CURRENT_TIMESTAMP"),
    #         server_onupdate=text("CURRENT_TIMESTAMP"),
    #     )
    # )


class ExperienceModel(SQLModel):
    company: str
    position: str
    description: str
    # start_date: DateTime = Field(
    #     sa_column=Column(
    #         TIMESTAMP(timezone=True),
    #         nullable=False,
    #         server_default=text("CURRENT_TIMESTAMP"),
    #         server_onupdate=text("CURRENT_TIMESTAMP"),
    #     )
    # )
    # end_date: DateTime = Field(
    #     sa_column=Column(
    #         TIMESTAMP(timezone=True),
    #         nullable=False,
    #         server_default=text("CURRENT_TIMESTAMP"),
    #         server_onupdate=text("CURRENT_TIMESTAMP"),
    #     )
    # )


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    name: str
    description: str
    link: str


class ProjectModel(SQLModel):
    name: str
    description: str
    link: str


class SocialPlatform(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    name: str
    link: str


class SocialPlatformModel(SQLModel):
    name: str
    link: str


class ProfileInfoModel(SQLModel):
    profile: ProfileModel
    programming_languages: list[ProgrammingLanguageModel] | None
    languages: list[LanguageModel] | None
    tools: list[ToolModel] | None
    certificates: list[CertificateModel] | None
    charities: list[CharityModel] | None
    educations: list[EducationModel] | None
    experiences: list[ExperienceModel] | None
    projects: list[ProjectModel] | None
    social_platforms: list[SocialPlatformModel] | None


# locations: list[LocationModel] | None  # TODO: In the future make this priority list
