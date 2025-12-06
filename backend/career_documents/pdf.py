import os
from pathlib import Path
from typing import Literal

import aiofiles
import devtools
from sqlmodel import Session
from weasyprint import CSS, HTML

from backend.config import settings
from backend.database.crud import (
    get_candidate_data,
    get_user_preferences,
    save_job_entry,
)
from backend.database.models import (
    JobEntryModel,
    SkillsLLMResponse,
    UserModel,
)
from backend.llm.llm import send_req_to_llm
from backend.llm.prompts import load_prompt
from backend.logger import get_logger
from backend.schemas.llm_responses import CompanyDetails, CVOutput
from backend.scrapers.base_scraper import JobEntry

logger = get_logger()


async def load_template_and_styling() -> tuple[str, str]:
    html_template, styling = "", ""
    async with (
        aiofiles.open(settings.HTML_TEMPLATE_PATH, "r") as template_file,
        aiofiles.open(settings.STYLING_PATH, "r") as styling_file,
    ):
        html_template, styling = (
            await template_file.read(),
            await styling_file.read(),
        )

    return html_template, styling


async def create_cover_letter(
    user: UserModel, session: Session, job_entry: JobEntry, current_time: str
) -> str:
    if not job_entry.company_name:
        return ""

    if job_entry.company_url:
        pass

    company_details = await send_req_to_llm(
        prompt=await load_prompt(
            prompt_path="cover_letter:user:company_data_search",
            company_name=job_entry.company_name,
        ),
        model=CompanyDetails,
    )

    logger.debug(f"Company info: {devtools.pformat(company_details)}")

    cover_letter_path = (
        settings.CV_DIR_PATH
        / f"{job_entry.title}_{current_time}.pdf"  # TODO: change job_entry.title
    )

    return cover_letter_path


async def create_cv(
    user: UserModel,
    session: Session,
    job_entry: JobEntry,
    current_time: str,
    mode: Literal[
        "llm-generation", "llm-selection", "no-llm-generation", "user-specified"
    ] = "llm-selection",
) -> str:
    candidate_data = get_candidate_data(session=session, user=user)
    html_template, styling = await load_template_and_styling()
    cv = None

    if mode == "llm-generation":
        skills_chosen_by_llm = await send_req_to_llm(
            system_prompt=await load_prompt(
                prompt_path="cv:system:skill_selection"
            ),
            prompt=await load_prompt(
                prompt_path="cv:user:skill_selection",
                model=candidate_data,
                requirements=job_entry.requirements,
                duties=job_entry.duties,
                about_project=job_entry.about_project,
            ),
            model=SkillsLLMResponse,
        )
        cv = await send_req_to_llm(
            system_prompt=await load_prompt(
                prompt_path="cv:system:cv_generation"
            ),
            prompt=await load_prompt(
                prompt_path="cv:user:cv_generation",
                model=skills_chosen_by_llm,
                full_name=candidate_data.full_name,
                email=candidate_data.email,
                phone_number=candidate_data.phone_number,
                social_platforms=candidate_data.social_platforms,
            ),
            model=CVOutput,
        )
    elif mode == "llm-selection":
        skills_chosen_by_llm = await send_req_to_llm(
            system_prompt=await load_prompt(
                prompt_path="cv:system:skill_selection"
            ),
            prompt=await load_prompt(
                prompt_path="cv:user:skill_selection",
                model=candidate_data,
                requirements=job_entry.requirements,
                duties=job_entry.duties,
                about_project=job_entry.about_project,
            ),
            model=SkillsLLMResponse,
        )
        cv = await send_req_to_llm(
            prompt=await load_prompt(
                "cv:user:cv_insert_skills",
                model=skills_chosen_by_llm,
                full_name=candidate_data.full_name,
                email=candidate_data.email,
                phone_number=candidate_data.phone_number,
                social_platforms=candidate_data.social_platforms,
                template=html_template,
            ),
            model=CVOutput,
        )
    elif mode == "no-llm-generation":
        raise NotImplementedError(
            "no-llm-generation option is not fully implemented yet"
        )
        # html = html_template.format(
        #     full_name=candidate_data.full_name,
        #     email=candidate_data.email,
        #     phone_number=candidate_data.phone_number,
        #     github=,
        #     linkedin=,
        #     personal_website=,
        # )
        # cv = CVOutput(html=html, css=styling)
    elif mode == "user-specified":
        if user_preferences := get_user_preferences(session, user):
            return Path(user_preferences.cv_path).as_uri()
        raise Exception("Could not load or create/generate CV")

    cv_path = (
        settings.CV_DIR_PATH
        / f"{job_entry.title}_{current_time}.pdf"  # TODO: change job_entry.title
    ).as_uri()

    if not os.path.isdir(settings.CV_DIR_PATH):
        os.mkdir(settings.CV_DIR_PATH)

    HTML(string=cv.html).write_pdf(cv_path, stylesheets=[CSS(string=cv.css)])

    return cv_path


async def generate_career_documents(
    user: UserModel,
    session: Session,
    job_entry: JobEntry,
    current_time: str,
    mode: Literal[
        "llm-generation", "llm-selection", "no-llm-generation", "user-specified"
    ] = "llm-selection",
) -> JobEntryModel:
    job_entry.cv_path = await create_cv(
        user=user,
        session=session,
        job_entry=job_entry,
        current_time=current_time,
        mode=mode,
    )
    job_entry.cover_letter_path = await create_cover_letter(
        user=user,
        session=session,
        job_entry=job_entry,
        current_time=current_time,
    )
    job_entry_model = save_job_entry(
        session=session, user=user, job_entry=job_entry
    )
    return job_entry_model
