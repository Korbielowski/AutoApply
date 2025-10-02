from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
from sqlmodel import select

from backend.database.models import (
    Certificate,
    Charity,
    Education,
    Experience,
    Language,
    Location,
    ProfileInfo,
    ProfileModel,
    ProgrammingLanguage,
    Project,
    SocialPlatform,
    Tool,
)
from backend.routes.deps import SessionDep

router = APIRouter(tags=["users"])
templates = Jinja2Templates(directory="templates")


@router.get("/login")
async def load_login_page(session: SessionDep, request: Request):
    profiles = session.exec(select(ProfileModel))
    return templates.TemplateResponse(
        request=request, name="login.html", context={"profiles": profiles}
    )


@router.post("/login")
async def login(session: SessionDep, request: Request, email: str = Form(...)):
    # TODO: Get current profile in other/better way ;)
    global profile
    profile = session.exec(
        select(ProfileModel).where(ProfileModel.email == email)
    ).first()
    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/register")
async def load_register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register")
async def register(
    session: SessionDep, request: Request, form_data: ProfileInfo
) -> RedirectResponse:  # form: Annotated[TestInfo, Form()]
    logger.info("cos dziala")
    d = {
        "locations": Location,
        "programming_languages": ProgrammingLanguage,
        "languages": Language,
        "tools": Tool,
        "certificates": Certificate,
        "charities": Charity,
        "educations": Education,
        "experience": Experience,
        "projects": Project,
        "social_platforms": SocialPlatform,
    }
    logger.info("Nadal dziala")
    form_dump = form_data.model_dump()
    form_profile = ProfileModel.model_validate(form_dump.get("profile"))

    logger.info("Juz nie dziala")
    models = []
    for key, val in d.items():
        tmp = form_dump.get(key, [])
        for t in tmp:
            models.append(val.model_validate(t))

    session.add(form_profile)
    session.commit()
    global profile
    profile = session.exec(
        select(ProfileModel).where(ProfileModel.email == form_profile.email)
    ).first()
    for model in models:
        model.profile_id = profile.id
        session.add(model)
    session.commit()
    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )
