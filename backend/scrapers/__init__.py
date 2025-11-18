import os
from pathlib import Path
from typing import Any, AsyncGenerator

from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from sqlmodel import Session

from backend.database.models import UserModel
from backend.logging import get_logger
from backend.pdf import create_cv
from backend.scrapers.llm_scraper import LLMScraper

logger = get_logger()


async def find_job_entries(
    user: UserModel,
    session: Session,
    websites,
    auto_apply: bool = False,
    generate_cv: bool = False,
    use_user_cv: bool = False,
) -> AsyncGenerator[str, Any]:
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
                        if not use_user_cv:
                            cv = create_cv(
                                user=user,
                                session=session,
                                job_entry=job_data,
                                mode="llm-selection",
                            )
                        else:
                            path = os.getenv("USER_CV", "")
                            if not path:
                                logger.error(
                                    "USER_CV variable with path to user's cv is not set"
                                )
                                yield f"data:{job_data}\n\n"
                            cv = Path(path)
                        logger.info(cv)
                    # TODO: Create CV in here and then apply ;)
                    if job_data:
                        logger.error("Sending data to client")
                        yield f"data:{job_data.model_dump_json()}\n\n"
                    else:
                        logger.error("Sending just nothing to client")
                        yield "data:null\n\n"
                running = await scraper.navigate_to_next_page()
                logger.info(f"Running: {running}")
                running = False


__all__ = ["find_job_entries"]
