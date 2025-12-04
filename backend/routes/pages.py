from typing import Union

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import func, select

from backend.config import settings
from backend.database.crud import get_job_entries
from backend.database.models import UserModel, WebsiteModel
from backend.logger import get_logger
from backend.routes.deps import CurrentUser, SessionDep
from backend.scrapers import find_job_entries

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(settings.ROOT_DIR / "templates")
logger = get_logger()


@router.get("/", response_class=Union[RedirectResponse, HTMLResponse])
async def index(
    current_user: CurrentUser, session: SessionDep, request: Request
):
    if not current_user:
        if session.scalar(func.count(UserModel.id)) >= 1:
            return RedirectResponse(
                url=request.url_for("load_login_page"),
                status_code=status.HTTP_303_SEE_OTHER,
            )
        return RedirectResponse(
            url=request.url_for("load_register_page"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    scraped_job_entries = get_job_entries(session, current_user)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": current_user,
            "scraped_job_entries": scraped_job_entries,
        },
    )


@router.get("/scrape_jobs", response_class=StreamingResponse)
async def scrape_jobs(current_user: CurrentUser, session: SessionDep):
    websites = session.exec(
        select(WebsiteModel).where(WebsiteModel.user_id == current_user.id)
    ).all()
    return StreamingResponse(
        content=find_job_entries(
            user=current_user, session=session, websites=websites
        ),
        media_type="text/event-stream",
    )


@router.get("/cv_page", response_class=HTMLResponse)
async def cv_page(
    current_user: CurrentUser, session: SessionDep, request: Request
):
    return


@router.get("/upload_cv", response_class=HTMLResponse)
async def upload_cv(
    current_user: CurrentUser, session: SessionDep, request: Request
):
    return
    # return templates.TemplateResponse(
    #     request=request, name="cv_page.html", context={"user": current_user}
    # )
