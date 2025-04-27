import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# from models import Profile
from sqlalchemy import URL, Engine
from sqlmodel import SQLModel, create_engine

# TODO: Check if user can specify custom drivers, so that they would not break SQLAlchemy
DRIVERNAME = "postgresql"
engine: Engine
OPENAI_API_KEY: str | None


# This will be used in the future for loading postgre and other stuff
@asynccontextmanager
async def setup(app: FastAPI) -> AsyncGenerator:
    username = os.environ.get("POSTGRE_USERNAME")
    password = os.environ.get("POSTGRE_PASSWORD")
    host = os.environ.get("POSTGRE_HOST")
    database = os.environ.get("POSTGRE_DATABASE")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    # TODO: This may be changed in the future or maybe stay the same?
    if not username:
        raise Exception("POSTGRE_USERNAME environmental variable not specified")
    if not password:
        raise Exception("POSTGRE_PASSWORD environmental variable not specified")
    if not host:
        raise Exception("POSTGRE_HOST environmental variable not specified")
    if not database:
        raise Exception("POSTGRE_PASSWORD environmental variable not specified")
    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY environmental variable not specified")

    url_oject = URL(
        drivername=DRIVERNAME,
        username=username,
        password=password,
        host=host,
        database=database,
    )
    engine = create_engine(
        url_oject, echo=True
    )  # TODO: Remove 'echo' parameter when releasing
    SQLModel.metadata.create_all(engine)

    yield

    # TODO: In the future release all resources


app = FastAPI(debug=True)  # TODO: FastAPI(debug=True, lifespan=setup)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
