from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import func

from backend.database.models import Profile, ProfileModel
from backend.routes.deps import SessionDep
from backend.scrapers import find_job_entries

router = APIRouter(tags=["pages"])
templates = Jinja2Templates("templates")

profile: None | Profile = None


@router.get("/")
async def index(session: SessionDep, request: Request):
    if profile is None:
        profile_count = session.scalar(func.count(ProfileModel.id))
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


@router.get("/scrape_jobs")
async def scrape_jobs(request: Request):
    return StreamingResponse(
        find_job_entries(
            profile,
            [
                "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3706084909"
            ],
        ),
        media_type="text/event-stream",
    )
