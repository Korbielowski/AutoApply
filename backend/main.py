from .app_setup import app, templates, engine
from sqlmodel import Session
from .models import (
    ProfileInfoModel,
    # Profile,
    # Language,
    # ProgrammingLanguage,
    # Tool,
    # Certificate,
    # Charity,
    # Education,
    # Experience,
    # Project,
    # SocialPlatform,
)
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse


@app.get("/", response_class=HTMLResponse)
# @authenticate_user
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/user_creation", response_class=HTMLResponse)
async def load_user_form(request: Request):
    return templates.TemplateResponse(request=request, name="user_creation.html")


@app.post("/user_creation", response_class=RedirectResponse)
async def create_user(request: Request, profile_information: ProfileInfoModel):
    with Session(engine) as session:
        info_validated = (
            i.__class__.model_validate(i) for i in profile_information.model_dump()
        )
        session.add_all(info_validated)
        session.commit()
        # session.refresh()
    return RedirectResponse(url=request.url_for("index"))
