import asyncio
from playwright.async_api import async_playwright, Playwright, Page, Locator
from sqlmodel import Session, select
from dotenv import load_dotenv

from app_setup import enigne
from models import JobEntry

import os
import re
import json
import logging

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


load_dotenv()
USER_EMAIL = os.getenv("USER_EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")


async def _init_playwright_page(playwright: Playwright) -> Page:
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()

    return page


async def apply_for_job_entry(page: Page) -> None:
    pass

# TODO: Add ability to log into many pages
async def _login_to_page(page: Page, link: str) -> None:
    await page.goto(link)
    await page.wait_for_load_state("load")
    await page.get_by_label("Email or phone").fill(USER_EMAIL)
    await page.get_by_label("Password").fill(PASSWORD)
    await page.get_by_label("Sign in").last.click()
    await page.wait_for_load_state("load")
    # TODO: Add functionality to check whether we got verification code on gmail


async def _get_job_entries(page: Page) -> tuple[Locator, ...]:
    pass


async def _process_job_entry(page: Page, locator: Locator = None, retry: int = 3) -> None:
    data = None

    # TODO: Make this loop make more sense, by maybe doing something more
    while data is None:
        if retry <= 0:
            logger.error("Cannot get information about job entry")
            break
        page_content = await page.content()
        data = re.search(r"{\"data\":{\"dashEntityUrn\":.*}", page_content)
        retry -= 1

    job_data = json.loads(data.group())
    posting_id = int(job_data["data"]["jobPostingId"])
    # TODO: Check if job id is already in database, if so, go to next job entry
    # with Session(engine) as session:
    #     stmt = select(JobEntry).where(JobEntry.posting_id == posting_id)
    #     result = session.exec(stmt)
    #     if not result:
    #         logger.error("Job posting is already in database")

    description = job_data["data"]["description"]
    location = job_data["data"]["formattedLocation"]
    company_url = job_data["data"]["applyMethod"]["companyApplyUrl"]

    logging.info(f"job posting id: {posting_id}")
    # logging.info(description)
    # logging.info(location)
    # logging.info(company_url)

    # with open("output.json", "w") as file:
    #     file.write(json.dumps(job_data, indent=4))


async def _go_to_next_page(page: Page) -> bool:
    pass


async def find_job_entries(page: Page, link: str) -> None:
    await _login_to_page(page, link)

    await _process_job_entry(page)
    # running = True
    # while running:
    #     for job_locator in await _get_job_entries(page):
    #         await _parse_job_entry(page, job_locator)
    #
    #     running = await _go_to_next_page()


# TODO: Add link: str parameter to this function
async def _run_scraper() -> None:
    async with async_playwright() as playwright:
        page = await _init_playwright_page(playwright)
        await find_job_entries(
            page,
            "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3706084909",
        )


if __name__ == "__main__":
    asyncio.run(_run_scraper())
