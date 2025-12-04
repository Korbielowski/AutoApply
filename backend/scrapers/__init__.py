from typing import Any, AsyncGenerator, Literal

from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from sqlmodel import Session

from backend.career_documents.pdf import create_cv
from backend.database.crud import save_job_entry
from backend.database.models import UserModel
from backend.logger import get_logger
from backend.scrapers.llm_scraper import LLMScraper

logger = get_logger()


async def find_job_entries(
    user: UserModel,
    session: Session,
    websites,
    cv_creation_mode: Literal[
        "llm-generation", "llm-selection", "no-llm-generation", "user-specified"
    ] = "llm-generation",
    auto_apply: bool = False,
) -> AsyncGenerator[str, Any]:
    if not websites:
        yield "data:null\n\n"

    async with Stealth().use_async(async_playwright()) as playwright:
        # TODO: Add ability for users to choose their preferred browser, recommend and default to chromium
        browser = await playwright.chromium.launch(headless=False)
        # TODO: Move code below to the for loop
        context = await browser.new_context(locale="en-US")
        # context.add_cookies()
        page = await context.new_page()

        for website in websites:
            logger.info(website)
            scraper = LLMScraper(
                url=website.url,
                email=website.user_email,
                password=website.user_password,
                context=context,
                page=page,
                website_info=website,
            )
            await scraper.login_to_page()

            running = True
            while running:
                for job in await scraper.get_job_entries():
                    job_data = await scraper.process_and_evaluate_job(job)
                    if job_data:
                        cv_path = await create_cv(
                            user=user,
                            session=session,
                            job_entry=job_data,
                            mode=cv_creation_mode,
                        )
                        job_data.cv_path = cv_path.as_uri()
                        job_entry_model = save_job_entry(
                            session=session, user=user, job_entry=job_data
                        )
                        yield f"data:{job_entry_model.model_dump_json()}\n\n"
                running = await scraper.navigate_to_next_page()


__all__ = ["find_job_entries"]
