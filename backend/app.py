# from .app_setup import engine, app, templates
from backend.app_setup import profile, app, templates
from backend.scrapers import find_job_entries
from backend.models import (
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

from fastapi import Request, Form, status
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlmodel import Session

from sqlalchemy import URL, func
from sqlmodel import SQLModel, create_engine, select
from dotenv import load_dotenv

import os
# from typing import Union


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


# @authenticate_user
# @app.get("/", response_model=Union[RedirectResponse, Jinja2Templates])
@app.get("/")
async def index(request: Request):
    if profile is None:
        with Session(engine) as session:
            profile_count = session.scalar(func.count(Profile.id))
            if profile_count > 0:
                return RedirectResponse(
                    url=request.url_for("load_login_page"),
                    status_code=status.HTTP_303_SEE_OTHER,
                )
        return RedirectResponse(
            url=request.url_for("load_register_page"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/login")
async def load_login_page(request: Request):
    with Session(engine) as session:
        profiles = session.exec(select(Profile))
        return templates.TemplateResponse(
            request=request, name="login.html", context={"profiles": profiles}
        )


@app.post("/login")
async def login(request: Request, email: str = Form(...)):
    with Session(engine) as session:
        global profile
        profile = session.exec(select(Profile).where(Profile.email == email)).first()
    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/register")
async def load_register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@app.post("/register")
async def register(
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
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/scrape_jobs")
async def scrape_jobs(request: Request):
    # await run_scraper(profile)
    return StreamingResponse(
        find_job_entries(
            profile,
            [
                "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3706084909"
            ],
        ),
        media_type="text/event-stream",
    )
