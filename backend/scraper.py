import asyncio
from playwright.async_api import async_playwright, Playwright


async def run(playwright: Playwright):
    chrome = playwright.chromium
    browser = await chrome.launch(headless=False)
    page = await browser.new_page()
    await page.goto(
        "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3706084909"
    )

    with open("file.txt", "w") as f:
        c = await page.content()
        f.write(c)
    await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)


if __name__ == "__main__":
    asyncio.run(main())
