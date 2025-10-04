from typing import Union

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from backend.database.models import User
from backend.routes.deps import CurrentUser
from backend.scrapers import find_job_entries

router = APIRouter(tags=["pages"])
templates = Jinja2Templates("templates")

profile: None | User = None


@router.get("/", response_class=Union[RedirectResponse, HTMLResponse])
async def index(current_user: CurrentUser, request: Request):
    if not current_user:
        return RedirectResponse(
            url=request.url_for("load_register_page"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return templates.TemplateResponse(request=request, name="index.html")


@router.get("/scrape_jobs", response_class=StreamingResponse)
async def scrape_jobs():
    return StreamingResponse(
        find_job_entries(
            profile,
            [
                "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3706084909"
            ],
        ),
        media_type="text/event-stream",
    )
