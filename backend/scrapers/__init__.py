from .pracuj_pl import PracujPl
from .linkedin import LinkedIn
from .llm_scraper import LLMScraper
from .base_scraper import BaseScraper

from playwright_stealth import Stealth
from playwright.async_api import async_playwright
from dotenv import load_dotenv
# from loguru import logger

from ..models import ProfileModel

from types import AsyncGeneratorType
from typing import Type
import os

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
) -> AsyncGeneratorType:
    async with Stealth().use_async(async_playwright()) as playwright:
        playwright.selectors.set_test_id_attribute("data-control-id")
        browser = await playwright.chromium.launch(headless=False)
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
                page=page,
                auto_apply=auto_apply,
                generate_cv=generate_cv,
            )
            await scraper.login_to_page()

            running = True
            while running:
                for job in await scraper.get_job_entires():
                    job_data = await scraper.process_job(job)
                    yield f"data:{job_data}\n\n"
                running = await scraper.go_to_next_page()


__all__ = ["find_job_entries"]
