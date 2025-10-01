import os
from pathlib import Path
from typing import Any, AsyncGenerator, Type

from dotenv import load_dotenv
from loguru import logger
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from ..models import ProfileModel
from ..pdf import create_cv
from .base_scraper import BaseScraper
from .linkedin import LinkedIn
from .llm_scraper import LLMScraper
from .pracuj_pl import PracujPl

load_dotenv()
USER_EMAIL = os.getenv("USER_EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")
SCRAPERS: dict[str, Type[BaseScraper]] = {
    "pracuj.pl": PracujPl,
    "linkedin.com": LinkedIn,
}


async def find_job_entries(
    profile: ProfileModel,
    links: list[str],
    auto_apply: bool = False,
    generate_cv: bool = False,
    use_llm: bool = False,
    use_user_cv: bool = False,
) -> AsyncGenerator[str, Any]:
    async with Stealth().use_async(async_playwright()) as playwright:
        # TODO: Add ability for users to choose their preferred browser, recommend and default to chromium
        playwright.selectors.set_test_id_attribute("data-control-id")
        browser = await playwright.chromium.launch(headless=False)
        # TODO: Maybe try using context: context = await browser.new_context()
        # context.add_cookies()
        page = await browser.new_page(locale="en-US")

        for link in links:
            sc: Type[BaseScraper] = (
                LLMScraper if use_llm else SCRAPERS.get("linkedin.com", LLMScraper)
            )
            # TODO: Replace with this --> SCRAPERS.get(link, LLMScraper)
            scraper = sc(
                link=link,
                profile=profile,
                email=USER_EMAIL,
                password=PASSWORD,
                browser=browser,
                page=page,
                auto_apply=auto_apply,
                generate_cv=generate_cv,
            )
            await scraper.login_to_page()

            running = True
            while running:
                for job in await scraper.get_job_entries():
                    job_data = await scraper.process_and_evaluate_job(job)
                    if job_data:
                        # TODO: Add use_own_cv flag to options
                        if not use_user_cv:
                            cv = create_cv(
                                profile,
                                job_data,
                                "llm-selection",
                            )
                        else:
                            path = os.getenv("USER_CV", "")
                            if not path:
                                logger.error(
                                    "USER_CV variable with path to user's cv is not set"
                                )
                                # TODO: Do not return information if job is not valuable
                            cv = Path(path)
                        logger.info(cv)
                        # TODO: Create CV in here and then apply ;)
                    yield f"data:{job_data}\n\n"
                running = await scraper.go_to_next_page()


__all__ = ["find_job_entries"]
