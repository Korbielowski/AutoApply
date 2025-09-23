from playwright.async_api import Page, Locator, TimeoutError
from loguru import logger


async def goto(page: Page, link: str, retry: int = 3, debug: bool = False) -> None:
    done = False
    while not done and retry > 0:
        try:
            await page.goto(link)
            done = True
        except TimeoutError as e:
            logger.exception(e)
        retry -= 1


async def click(element: Locator, retry: int = 3, debug: bool = False) -> None:
    done = False
    while not done and retry > 0:
        try:
            if debug:
                await element.highlight()
            await element.click()
            done = True
        except TimeoutError as e:
            logger.exception(e)
        retry -= 1


async def fill(
    element: Locator, value: str, retry: int = 3, debug: bool = False
) -> None:
    done = False
    while not done and retry > 0:
        try:
            if debug:
                await element.highlight()
            await element.fill(value)
            done = True
        except TimeoutError as e:
            logger.exception(e)
        retry -= 1
