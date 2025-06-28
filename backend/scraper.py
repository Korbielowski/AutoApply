import asyncio
from playwright.async_api import async_playwright, Playwright, Page, Locator
from dotenv import load_dotenv

import os
import re
import json


load_dotenv()
USER_EMAIL = os.getenv("USER_EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")


async def _init_playwright_page(playwright: Playwright) -> Page:
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()

    return page


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


async def _process_job_entry(page: Page, locator: Locator = None) -> None:
    # TODO: Check if job id is already in database, if so, go to next job entry
    content = await page.content()

    job_data = json.loads(re.search(r"{\"data\":{\"dashEntityUrn\":.*}", content))
    with open("output.json", "w") as file:
        file.write(job_data)


async def _go_to_next_page(page: Page) -> bool:
    pass


async def find_job_entries(page: Page, link: str) -> None:
    await _login_to_page(page, link)

    _process_job_entry(page)
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
