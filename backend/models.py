from sqlmodel import Field, DateTime, SQLModel


class Profile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    middlename: str
    surname: str
    age: int


class ProgrammingLanguage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key=True)
    language: str
    level: str  # Maybe in the future change to int


class Language(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key=True)
    language: str
    level: str  # Maybe in the future change to int


class Tool(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key=True)
    name: str
    level: str  # Maybe in the future change to int


class Certificate(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key=True)
    name: str
    description: str
    organisation: str


class Charity(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key=True)
    name: str
    description: str
    organistaion: str
    start_date: DateTime
    end_date: DateTime


class Education(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key=True)
    school: str
    major: str
    description: str
    start_date: DateTime
    end_date: DateTime


class Experience(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key=True)
    company: str
    position: str
    description: str
    start_date: DateTime
    end_date: DateTime


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key=True)
    name: str
    description: str
    link: str


class SocialPlatform(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key=True)
    name: str
    link: str
