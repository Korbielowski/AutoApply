from typing import Union

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import func, select

from backend.database.crud import create_user
from backend.database.models import (
    CertificateModel,
    CharityModel,
    EducationModel,
    ExperienceModel,
    LanguageModel,
    LocationModel,
    ProfileInfo,
    ProgrammingLanguageModel,
    ProjectModel,
    SocialPlatformModel,
    ToolModel,
    UserModel,
)
from backend.routes.deps import SessionDep, set_current_user

router = APIRouter(tags=["users"])
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def load_login_page(session: SessionDep, request: Request):
    profiles = session.exec(select(UserModel))
    return templates.TemplateResponse(
        request=request, name="login.html", context={"profiles": profiles}
    )


@router.post("/login", response_class=RedirectResponse)
async def login(session: SessionDep, request: Request, email: str = Form(...)):
    # TODO: Get current profile in other/better way ;)
    set_current_user(session, email)
    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/register", response_class=Union[RedirectResponse, HTMLResponse])
async def load_register_page(session: SessionDep, request: Request):
    if session.scalar(func.count(UserModel.id)) >= 1:
        return RedirectResponse(
            url=request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER
        )
    return templates.TemplateResponse(request=request, name="register.html")  # type: ignore


@router.post("/register", response_class=RedirectResponse)
async def register(
    session: SessionDep,
    request: Request,
    form_data: ProfileInfo,  # form: Annotated[TestInfo, Form()]
):
    d = {
        "locations": LocationModel,
        "programming_languages": ProgrammingLanguageModel,
        "languages": LanguageModel,
        "tools": ToolModel,
        "certificates": CertificateModel,
        "charities": CharityModel,
        "educations": EducationModel,
        "experience": ExperienceModel,
        "projects": ProjectModel,
        "social_platforms": SocialPlatformModel,
    }
    form_dump = form_data.model_dump()
    user = UserModel.model_validate(form_dump.get("profile"))

    models = []
    for key, val in d.items():
        tmp = form_dump.get(key, [])
        for t in tmp:
            models.append(val.model_validate(t))

    user = create_user(session, user)

    for model in models:
        model.user_id = user.id
        session.add(model)
    session.commit()

    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )
