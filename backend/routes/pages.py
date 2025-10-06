from typing import Union

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from backend.routes.deps import CurrentUser, SessionDep
from backend.scrapers import find_job_entries

router = APIRouter(tags=["pages"])
templates = Jinja2Templates("templates")


@router.get("/", response_class=Union[RedirectResponse, HTMLResponse])
async def index(current_user: CurrentUser, request: Request):
    if not current_user:
        return RedirectResponse(
            url=request.url_for("load_register_page"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return templates.TemplateResponse(request=request, name="index.html")


@router.get("/scrape_jobs", response_class=StreamingResponse)
async def scrape_jobs(current_user: CurrentUser, session: SessionDep):
    # TODO: Get sites/urls to scrape from database and user/website form
    # TODO: Get program options like generate_cv from database and user/website form
    return StreamingResponse(
        find_job_entries(
            user=current_user,
            session=session,
            urls=[
                "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3706084909"
            ],
        ),
        media_type="text/event-stream",
    )
