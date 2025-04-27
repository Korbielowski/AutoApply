from typing import Optional

from sqlmodel import Field, SQLModel


class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    password: str


class ProfileInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    location_id: Optional[int] = Field(default=None, foreign_key=True)


class ProfileLocationInfo(SQLModel, table=True):
    location_id: Optional[int] = Field(default=None, primary_key=True)
    country: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]


class ProfileLanguageInfo(SQLModel, table=True):
    language_id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: Optional[int] = Field(default=None, foreign_key=True)
    language: Optional[str]
    proficiency: Optional[str]
