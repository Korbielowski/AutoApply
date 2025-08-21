from .pracuj_pl import PracujPl
from .linkedin import LinkedIn
from .llm_scraper import LLMScraper
from .base_scraper import BaseScraper

from playwright_stealth import Stealth
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from loguru import logger

from ..models import ProfileModel

import sys
import os

logger.add(sys.stdout, colorize=True)
load_dotenv()
USER_EMAIL = os.getenv("USER_EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")
SCRAPERS = {"pracuj.pl": PracujPl, "linkedin.com": LinkedIn}


async def find_job_entries(
    profile: ProfileModel,
    links: list[str],
    auto_apply: bool = False,
    generate_cv: bool = False,
    use_llm: bool = False,
) -> str:
    async with Stealth().use_async(async_playwright()) as playwright:
        playwright.selectors.set_test_id_attribute("data-control-id")
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page(locale="en-US")

        for link in links:
            if use_llm:
                scraper: BaseScraper = LLMScraper
            else:
                # scraper: BaseScraper = SCRAPERS.get(link, LLMScraper)
                scraper: BaseScraper = SCRAPERS.get("linkedin.com")
            scraper = scraper(
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


__all__ = ["find_job_entries"]
