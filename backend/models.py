from sqlmodel import Column, Field, DateTime, SQLModel, TIMESTAMP, text


class Profile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    middlename: str
    surname: str
    age: int


class ProfileModel(SQLModel):
    name: str
    middlename: str
    surname: str
    age: int


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
    organistaion: str
    start_date: DateTime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )
    end_date: DateTime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )


class CharityModel(SQLModel):
    name: str
    description: str
    organistaion: str
    start_date: DateTime
    end_date: DateTime


class Education(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    school: str
    major: str
    description: str
    start_date: DateTime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )
    end_date: DateTime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )


class EducationModel(SQLModel):
    school: str
    major: str
    description: str
    start_date: DateTime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )
    end_date: DateTime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )


class Experience(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key="profile.id")
    company: str
    position: str
    description: str
    start_date: DateTime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )
    end_date: DateTime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )


class ExperienceModel(SQLModel):
    company: str
    position: str
    description: str
    start_date: DateTime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )
    end_date: DateTime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )


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
    programming_language: list[ProgrammingLanguageModel] | None
    language: list[LanguageModel] | None
    tool: list[ToolModel] | None
    certificate: list[CertificateModel] | None
    charity: list[CharityModel] | None
    education: list[EducationModel] | None
    experience: list[ExperienceModel] | None
    project: list[ProjectModel] | None
    social_platform: list[SocialPlatformModel] | None
