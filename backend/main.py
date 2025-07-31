# from .app_setup import engine, app, templates
from .app_setup import app, templates
from .scraper import find_job_entries
from .models import (
    ProfileInfoModel,
    Profile,
    Location,
    ProgrammingLanguage,
    Language,
    Tool,
    Certificate,
    Charity,
    Education,
    Experience,
    Project,
    SocialPlatform,
)

from fastapi import Request, status
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlmodel import Session

from sqlalchemy import URL
from sqlmodel import SQLModel, create_engine, select
from dotenv import load_dotenv

import os


DRIVERNAME = "postgresql+psycopg"
load_dotenv()
username = os.environ.get("POSTGRE_USERNAME")
password = os.environ.get("POSTGRE_PASSWORD")
host = os.environ.get("POSTGRE_HOST")
database = os.environ.get("POSTGRE_DATABASE")


url_object = URL.create(
    drivername=DRIVERNAME,
    username=username,
    password=password,
    host=host,
    database=database,
)
engine = create_engine(url_object)  # TODO: Remove 'echo' parameter when releasing
SQLModel.metadata.create_all(engine)
profile = None


@app.get("/")
# @authenticate_user
async def root(request: Request) -> RedirectResponse:
    return RedirectResponse(url=request.url_for("load_user_form"))
    # return templates.TemplateResponse(request=request, name="index.html")


@app.get("/create_user")
async def load_user_form(request: Request):
    return templates.TemplateResponse(request=request, name="create_user.html")


@app.post("/create_user")
async def create_user(
    request: Request, form_data: ProfileInfoModel
) -> RedirectResponse:  # form: Annotated[TestInfo, Form()]
    d = {
        "locations": Location,
        "programming_languages": ProgrammingLanguage,
        "languages": Language,
        "tools": Tool,
        "certificates": Certificate,
        "charities": Charity,
        "educations": Education,
        "exprience": Experience,
        "projects": Project,
        "social_platforms": SocialPlatform,
    }
    form_dump = form_data.model_dump()
    form_profile = Profile.model_validate(form_dump.get("profile"))

    models = []
    for key, val in d.items():
        tmp = form_dump.get(key, [])
        for t in tmp:
            models.append(val.model_validate(t))

    with Session(engine) as session:
        session.add(form_profile)
        session.commit()
        global profile
        profile = session.exec(
            select(Profile).where(Profile.email == form_profile.email)
        ).first()
        for model in models:
            model.profile_id = profile.id
            session.add(model)
        session.commit()
    return RedirectResponse(
        url=request.url_for("panel"), status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/panel")
async def panel(request: Request):
    return templates.TemplateResponse(request=request, name="panel.html")


@app.get("/scrape_jobs")
async def scrape_jobs(request: Request):
    # await run_scraper(profile)
    return StreamingResponse(
        find_job_entries(
            profile,
            "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4254862954",
        ),
        media_type="text/event-stream",
    )
