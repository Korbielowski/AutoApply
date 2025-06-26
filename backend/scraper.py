import asyncio
from playwright.async_api import async_playwright, Playwright, Page
from dotenv import load_dotenv
import os

load_dotenv()
USER_EMAIL = os.getenv("USER_EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")


# TODO: Add ability to log into many pages
async def login_to_page(page: Page, link: str):
    page.goto(link)
    page.wait_for_load_state("load")
    # page.get_by_label("Email or phone").click()
    page.get_by_label("Email or phone").fill(USER_EMAIL)
    # page.get_by_label("Password").click()
    page.get_by_label("Password").fill(PASSWORD)


async def run(playwright: Playwright, link: str):
    chrome = playwright.chromium
    browser = await chrome.launch(headless=False)
    page = await browser.new_page()

    login_to_page(page, link)

    with open("file.txt", "w") as f:
        c = await page.content()
        f.write(c)
    await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(
            playwright,
            "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3706084909",
        )


if __name__ == "__main__":
    asyncio.run(main())
