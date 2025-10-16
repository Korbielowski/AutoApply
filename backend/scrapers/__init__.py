import os
from pathlib import Path
from typing import Any, AsyncGenerator

from loguru import logger
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from sqlmodel import Session, select

from backend.config import settings
from backend.database.models import UserModel, WebsiteModel
from backend.pdf import create_cv
from backend.scrapers.llm_scraper import LLMScraper


async def find_job_entries(
    user: UserModel,
    session: Session,
    urls: list[str],
    auto_apply: bool = False,
    generate_cv: bool = False,
    use_user_cv: bool = False,
) -> AsyncGenerator[str, Any]:
    async with Stealth().use_async(async_playwright()) as playwright:
        # TODO: Add ability for users to choose their preferred browser, recommend and default to chromium
        playwright.selectors.set_test_id_attribute("data-control-id")
        browser = await playwright.chromium.launch(headless=False)
        # TODO: Maybe try using context: context = await browser.new_context()
        # context.add_cookies()
        page = await browser.new_page(locale="en-US")

        for url in urls:
            website_info = session.exec(
                select(WebsiteModel).where(WebsiteModel.url == url)
            ).first()
            scraper = LLMScraper(
                url=url,
                email=settings.USER_EMAIL,
                password=settings.PASSWORD,
                browser=browser,
                page=page,
                website_info=website_info,
            )
            await scraper.login_to_page()

            running = True
            while running:
                for job in await scraper.get_job_entries():
                    job_data = await scraper.process_and_evaluate_job(job)
                    if job_data:
                        if not use_user_cv:
                            cv = create_cv(
                                user,
                                job_data,
                                "llm-selection",
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
                    yield f"data:{job_data}\n\n"
                running = await scraper.go_to_next_page()


__all__ = ["find_job_entries"]
