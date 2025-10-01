import os

from dotenv import load_dotenv
from sqlalchemy import URL, Engine
from sqlmodel import SQLModel, create_engine

# TODO: Check if user can specify custom drivers, so that they would not break SQLAlchemy
DRIVERNAME = "postgresql+psycopg"


def setup_database() -> Engine:
    load_dotenv("../.env")  # TODO: Path to .env is "../.env"
    username = os.environ.get("POSTGRES_USERNAME")
    password = os.environ.get("POSTGRES_PASSWORD")
    host = os.environ.get("POSTGRES_HOST")
    database = os.environ.get("POSTGRES_DATABASE")

    if not username:
        raise Exception("POSTGRES_USERNAME environmental variable not specified")
    if not password:
        raise Exception("POSTGRES_PASSWORD environmental variable not specified")
    if not host:
        raise Exception("POSTGRES_HOST environmental variable not specified")
    if not database:
        raise Exception("POSTGRES_PASSWORD environmental variable not specified")

    url_object = URL.create(
        drivername=DRIVERNAME,
        username=username,
        password=password,
        host=host,
        database=database,
    )

    eng = create_engine(url_object)  # TODO: Remove 'echo' parameter when releasing
    SQLModel.metadata.create_all(eng)

    return eng
