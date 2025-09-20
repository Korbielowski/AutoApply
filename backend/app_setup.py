import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy import URL, func
from sqlmodel import SQLModel, Session, create_engine, select
from dotenv import load_dotenv


from backend.models import Profile

# TODO: Check if user can specify custom drivers, so that they would not break SQLAlchemy
DRIVERNAME = "postgresql+psycopg"
# engine: Engine = None
API_KEY: str = ""
profile = None


# This will be used in the future for loading postgre and other stuff
@asynccontextmanager
async def setup(app: FastAPI) -> AsyncGenerator:
    global engine
    load_dotenv()  # TODO: Path to .env is "../.env"
    username = os.environ.get("POSTGRE_USERNAME")
    password = os.environ.get("POSTGRE_PASSWORD")
    host = os.environ.get("POSTGRE_HOST")
    database = os.environ.get("POSTGRE_DATABASE")
    API_KEY = os.environ.get("API_KEY", "")

    # WARNING: This will probably be changed in the future
    if not username:
        raise Exception("POSTGRE_USERNAME environmental variable not specified")
    if not password:
        raise Exception("POSTGRE_PASSWORD environmental variable not specified")
    if not host:
        raise Exception("POSTGRE_HOST environmental variable not specified")
    if not database:
        raise Exception("POSTGRE_PASSWORD environmental variable not specified")
    if not API_KEY:
        raise Exception("API_KEY environmental variable not specified")

    url_object = URL.create(
        drivername=DRIVERNAME,
        username=username,
        password=password,
        host=host,
        database=database,
    )
    engine = create_engine(url_object)  # TODO: Remove 'echo' parameter when releasing
    SQLModel.metadata.create_all(engine)

    # TODO: Fix login with one account
    with Session(engine) as session:
        profile_count = session.scalar(func.count(Profile.id))
        if profile_count == 1:
            global profile
            profile = session.exec(select(Profile)).first()

    yield

    # TODO: In the future release all resources


# app = FastAPI(debug=True, lifespan=setup)  # TODO: FastAPI(debug=True, lifespan=setup)
app = FastAPI(debug=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
