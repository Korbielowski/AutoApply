import asyncio
from playwright.async_api import async_playwright, Playwright, Page
from dotenv import load_dotenv
import os

load_dotenv()
USER_EMAIL = os.getenv("USER_EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")


# TODO: Add ability to log into many pages
async def login_to_page(page: Page, link: str) -> None:
    await page.goto(link)
    await page.wait_for_load_state("load")
    # page.get_by_label("Email or phone").click()
    await page.get_by_label("Email or phone").fill(USER_EMAIL)
    # page.get_by_label("Password").click()
    await page.get_by_label("Password").fill(PASSWORD)
    await page.get_by_label("Sign in").last.click()
    await page.wait_for_load_state("load")


async def scrape(playwright: Playwright, link: str) -> None:
    chrome = playwright.chromium
    browser = await chrome.launch(headless=False)
    page = await browser.new_page()

    await login_to_page(page, link)
    with open("linkedin.html", "w") as f:
        c = await page.content()
        f.write(c)
    await browser.close()


# TODO: Add link: str parameter to this function
async def run_scraper() -> None:
    async with async_playwright() as playwright:
        await scrape(
            playwright,
            "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3706084909",
        )


if __name__ == "__main__":
    asyncio.run(run_scraper())
