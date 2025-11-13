from typing import Union

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from backend.database.crud import create_user, delete_user
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
    WebsiteModel,
)
from backend.logging import get_logger
from backend.routes.deps import (
    CurrentUser,
    SessionDep,
    set_current_user,
)

router = APIRouter(tags=["users"])
templates = Jinja2Templates(directory="templates")
logger = get_logger()


@router.get("/login", response_class=HTMLResponse)
async def load_login_page(session: SessionDep, request: Request):
    users = session.exec(select(UserModel))
    return templates.TemplateResponse(
        request=request, name="login.html", context={"users": users}
    )


@router.post("/login", response_class=RedirectResponse)
async def login(session: SessionDep, request: Request, email: str = Form(...)):
    # TODO: Get current profile in other/better way ;)
    set_current_user(session, email)
    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/logout", response_class=RedirectResponse)
async def logout(session: SessionDep, request: Request):
    set_current_user(session, None)
    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/register", response_class=Union[RedirectResponse, HTMLResponse])
async def load_register_page(current_user: CurrentUser, request: Request):
    return templates.TemplateResponse(
        request=request, name="register.html", context={"user": current_user}
    )


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
        "websites": WebsiteModel,
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

    set_current_user(session, user.email)

    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/account", response_class=Union[HTMLResponse, HTMLResponse])
async def account_details(
    current_user: CurrentUser, session: SessionDep, request: Request
):
    if not current_user:
        return RedirectResponse(
            url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
        )
    context = {
        "user": current_user,
        "locations": session.exec(
            select(LocationModel).where(
                LocationModel.user_id == current_user.id
            )
        ),
        "programming_languages": session.exec(
            select(ProgrammingLanguageModel).where(
                ProgrammingLanguageModel.user_id == current_user.id
            )
        ),
        "languages": session.exec(
            select(LanguageModel).where(
                LanguageModel.user_id == current_user.id
            )
        ),
        "tools": session.exec(
            select(ToolModel).where(ToolModel.user_id == current_user.id)
        ),
        "certificates": session.exec(
            select(CertificateModel).where(
                CertificateModel.user_id == current_user.id
            )
        ),
        "charities": session.exec(
            select(CharityModel).where(CharityModel.user_id == current_user.id)
        ),
        "educations": session.exec(
            select(EducationModel).where(
                EducationModel.user_id == current_user.id
            )
        ),
        "experience": session.exec(
            select(ExperienceModel).where(
                ExperienceModel.user_id == current_user.id
            )
        ),
        "projects": session.exec(
            select(ProjectModel).where(ProjectModel.user_id == current_user.id)
        ),
        "social_platforms": session.exec(
            select(SocialPlatformModel).where(
                SocialPlatformModel.user_id == current_user.id
            )
        ),
        "websites": session.exec(
            select(WebsiteModel).where(WebsiteModel.user_id == current_user.id)
        ),
    }
    return templates.TemplateResponse(
        request=request, name="account.html", context=context
    )


@router.post(
    "/delete_account", response_class=Union[HTMLResponse, HTMLResponse]
)
async def delete_account(
    session: SessionDep, request: Request, email: str = Form(...)
):  # TODO: Try using EmailStr instead of plain str
    delete_user(session, email)
    set_current_user(session, None)

    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/edit_account", response_class=Union[HTMLResponse, HTMLResponse])
async def edit_account(
    session: SessionDep, request: Request, user: str = Form(...)
):
    logger.info(user)


@router.get("/manage_users", response_class=HTMLResponse)
async def load_manage_users_page(
    user: CurrentUser, session: SessionDep, request: Request
):
    users = session.exec(select(UserModel))

    return templates.TemplateResponse(
        request=request,
        name="manage_users.html",
        context={"user": user, "users": users},
    )
