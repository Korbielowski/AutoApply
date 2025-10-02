from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlmodel import Session, select

from backend.config import settings
from backend.database.db import engine, init_db
from backend.database.models import (
    UserModel,
)
from backend.routes.main import api_router

profile: UserModel


@asynccontextmanager
async def setup(inner_app: FastAPI) -> AsyncGenerator:
    init_db()

    # FIXME: Fix login with one account
    with Session(engine) as session:
        profile_count = session.scalar(func.count(UserModel.id))
        if profile_count == 1:
            global profile
            profile = session.exec(select(UserModel)).first()

    inner_app.mount("/static", StaticFiles(directory="static"), name="static")

    yield
    # TODO: In the future release all resources if needed


app = FastAPI(title=settings.PROJECT_NAME, debug=True, lifespan=setup)
app.include_router(api_router)
