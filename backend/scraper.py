from playwright.async_api import async_playwright, Playwright, Page, Locator
from playwright_stealth import Stealth
from dotenv import load_dotenv

from .llm import send_req_to_llm
from .pdf import create_cv
from .models import ProfileModel
from .scrapers import PracujPl, LinkedIn
# from app_setup import enigne
# from models import JobEntry

import asyncio
import os
import re
import json
import logging
from pathlib import Path


logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
load_dotenv()
USER_EMAIL = os.getenv("USER_EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")

SCRAPERS = {"pracuj.pl": PracujPl(), "linkedin.com": LinkedIn()}


async def _init_playwright_page(playwright: Playwright) -> Page:
    playwright.selectors.set_test_id_attribute("data-control-id")
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page(locale="en-US")

    return page


async def apply_for_job_entry(page: Page) -> None:
    pass


async def _login_to_page(page: Page, link: str) -> None:
    # TODO: Add functionality to check whether we got verification code on email or not
    if "linkedin.com" in link:
        await page.goto(link)
        await page.wait_for_load_state("load")
        await page.get_by_label("Email or phone").fill(USER_EMAIL)
        await page.get_by_label("Password").fill(PASSWORD)
        await page.get_by_label("Sign in").last.click()
        await page.wait_for_load_state("load")
    else:
        pass
        # TODO: Add ability to log into many pages using LLM


async def _get_job_entries(page: Page) -> tuple[Locator, ...]:
    pattern = re.compile(r".*")
    ld: dict = {}  # TODO: Check if set would be faster than dict
    max_scrolls = 20
    wheel_move = 200
    start_pos_x = (
        int(
            await page.evaluate(
                "Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0)"
            )
        )
        / 3
    )
    start_pos_y = int(
        await page.evaluate(
            "Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0)"
        )
        / 2
    )

    await page.mouse.move(start_pos_x, start_pos_y)

    # TODO: Find a better way for scrolling through the whole page (https://scrapfly.io/blog/answers/how-to-scroll-to-the-bottom-with-playwright)
    for _ in range(max_scrolls):
        locator = page.get_by_test_id(pattern)
        for i in range(await locator.count()):
            a_tag = locator.nth(i)
            href = await a_tag.get_attribute("href")
            if href not in ld:
                ld[href] = a_tag
        await page.mouse.wheel(0, wheel_move)
        await page.wait_for_timeout(500)
    return tuple(ld.values())


def _evaluate_job(description: str) -> tuple[bool, str]:
    # TODO: Make LLM compare user's skills with skills in the description
    prompt = f"Get only skills, qualifications, place required for this role from the description and return only them in your response and nothing more. {str(description)}"
    requirements = send_req_to_llm(prompt, temperature=0)
    logging.info(f"Important information about the posiotion: {requirements}")
    user_needs = (
        "C, Rust, Poland, Python 5+ years, CI/CD, GIT, python testing, fluent polish"
    )
    prompt = f"Compare my qualifications and needs: {user_needs}. With these from job offer: {requirements}. Return only one word, True if I should apply, and False if not and no other words/characters"
    response = send_req_to_llm(prompt + str(description), temperature=0)
    logging.info(f"LLM evalutaion: {response}")
    if "True" in response:
        return (True, requirements)
    else:
        return (False, requirements)


async def _process_job_entry(
    profile: ProfileModel, page: Page, locator: Locator = None, retry: int = 3
) -> str:
    data = None

    # TODO: Make this loop make more sense, by maybe doing something more
    while data is None:
        if retry <= 0:
            logging.error("Cannot get information about job entry")
            break
        page_content = await page.content()
        data = re.search(r"{\"data\":{\"dashEntityUrn\":.*}", page_content)
        retry -= 1

    if data is None:
        logging.error("Did not get information about the job entry")
        return ""

    job_data = json.loads(data.group())
    posting_id = int(job_data["data"]["jobPostingId"])
    logging.info(f"job posting id: {posting_id}")
    # TODO: Check if job id is already in database, if so, go to next job entry
    # with Session(engine) as session:
    #     hashed_id = hash(posting_id)
    #     stmt = select(JobEntry).where(JobEntry.posting_id == hashed_id)
    #     result = session.exec(stmt)
    #     if result:
    #         logger.error("Job posting is already in database")

    description = job_data.get("data", {}).get("description", {}).get("text", "")
    location = job_data.get("data", {}).get("formattedLocation", "")
    company_url = (
        job_data.get("data", {}).get("applyMethod", {}).get("companyApplyUrl", "")
    )

    # TODO: Evaluate job entry based on comparison between job's description and user's skills
    is_valuable, requirements = _evaluate_job(description)

    if is_valuable:
        logging.info("You should apply")
        # TODO: Add use_own_cv flag to options
        use_own_cv = False
        if not use_own_cv:
            cv = create_cv(
                profile,
                posting_id,
                requirements,
                location,
                company_url,
                "llm-selection",
            )
        else:
            path = os.getenv("USER_CV", "")
            if not path:
                logging.error("USER_CV variable with path to user's cv is not set")
                return
            cv = Path(path)
            logging.info(cv)
        # _apply_for_job(page, cv)
    else:
        logging.info("You should not apply")
    return json.dumps(
        {
            "posting_id": posting_id,
            "description": description,
            "location": location,
            "company_url": company_url,
        }
    )


async def _go_to_next_page(page: Page) -> bool:
    pass


async def _go_to_next_job(page: Page) -> bool:
    # if :
    #     if not _go_to_next_page(page):
    #         return False
    pass


async def find_job_entries(profile: ProfileModel, link: str) -> None:
    # scraper = SCRAPERS.get(link, LLMScraper())
    # scraper = SCRAPERS.get
    async with Stealth().use_async(async_playwright()) as playwright:
        page = await _init_playwright_page(playwright)
        # await scraper.login_to_page()
        await _login_to_page(page, link)
        # await _go_to_job_list(page)
        await _get_job_entries(page)
        # while True:
        #     await asyncio.sleep(1)
        yield "data:1\n\n"

        # running = True
        # while running:
        #     # for job_locator in await _get_job_entries(page):
        #     data = await _process_job_entry(profile, page)
        #     running = await _go_to_next_job()
        #     yield f"data:{data}\n\n"


# TODO: Add link: str parameter to this function
async def run_scraper(profile: ProfileModel, link: str = "") -> None:
    async with async_playwright() as playwright:
        page = await _init_playwright_page(playwright)
        find_job_entries(
            profile,
            page,
            "",
        )


if __name__ == "__main__":
    asyncio.run(run_scraper())
