from sqlmodel import Field, SQLModel


class Profile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    password: str


class ProfileInfo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    location_id: int | None = Field(default=None, foreign_key=True)


class ProfileLocationInfo(SQLModel, table=True):
    location_id: int | None = Field(default=None, primary_key=True)
    country: str | None
    city: str | None
    postal_code: str | None


class ProfileLanguageInfo(SQLModel, table=True):
    language_id: int | None = Field(default=None, primary_key=True)
    profile_id: int | None = Field(default=None, foreign_key=True)
    language: str | None
    proficiency: str | None
