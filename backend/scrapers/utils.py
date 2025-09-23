from playwright.async_api import Page, Locator, TimeoutError
from bs4 import BeautifulSoup
from loguru import logger
import tiktoken

from backend.llm import send_req_to_llm

import json

TIK = tiktoken.encoding_for_model("gpt-5-")


async def goto(page: Page, link: str, retry: int = 3, debug: bool = False) -> None:
    done = False
    while not done and retry > 0:
        try:
            await page.goto(link)
            await page.wait_for_load_state("load")
            done = True
        except TimeoutError as e:
            logger.exception(e)
        retry -= 1


async def click(
    element: None | Locator, page: Page, retry: int = 3, debug: bool = False
) -> None:
    if not element:
        logger.exception("Could not find button")
        return

    done = False
    while not done and retry > 0:
        try:
            if debug:
                await element.highlight()
            await element.click()
            await page.wait_for_load_state("load")
            done = True
        except TimeoutError as e:
            logger.exception(e)
        retry -= 1


async def fill(
    element: None | Locator, value: str, retry: int = 3, debug: bool = False
) -> None:
    if not element:
        logger.error("Could not find input field")
        return

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


async def get_page_content(page: Page) -> str:
    # TODO: Make page content smaller by e.g. excluding head or code tags and only by including body
    # TODO: Check in the future, whether regex would not be faster and overall better solution
    page_content = await page.content()
    logger.info(f"Amount of tokens before cleaning: {len(TIK.encode(page_content))}")
    soup = BeautifulSoup(page_content, "html.parser")
    for tag in soup(
        [
            "head",
            "meta",
            "style",
            "script",
            "noscript",
            "template",
            "iframe",
            "video",
            "audio",
            "map",
            "area",
            "embed",
            "object",
            "applet",
            "track",
            "canvas",
            "svg",
            "img",
            "picture",
            "source",
        ]
    ):
        tag.decompose()
        cleaned_page_content = str(soup)
    logger.info(
        f"Amount of tokens after cleaning: {len(TIK.encode(cleaned_page_content))}"
    )
    return cleaned_page_content


async def find_html_element_attributes(page: Page, prompt: str) -> None | dict:
    pre_prompt = "I will give you an HTML snippet."
    post_prompt = "Return only its identifying attributes in JSON format with the following keys: id, name, type, aria-label, placeholder, role, text, classList. If an attribute does not exist, return null for it. Do not explain, only return JSON"
    page_content = await get_page_content(page)
    prompt = f"{pre_prompt}{prompt}{post_prompt}\n{page_content}"

    response = await send_req_to_llm(
        prompt,
        use_openai=True,
    )

    try:
        attributes = json.loads(response)
        logger.info(f"List of attributes:\n{json.dumps(attributes, indent=2)}")
    except json.JSONDecodeError as e:
        logger.exception(e)
        return None

    return attributes


async def find_html_element(page: Page, prompt: str) -> None | Locator:
    attributes = await find_html_element_attributes(page, prompt)
    if not attributes:
        return None

    # TODO: Make sure that we are selecting only one element, especially true for "type" and "classList"
    id = attributes.get("id", "")
    locator = page.locator(f"#{id}")
    if await locator.count() != 0:
        return locator.last

    text = attributes.get("text", "")
    locator = page.get_by_text(text)
    if await locator.count() != 0:
        return locator.last

    aria_label = attributes.get("aria-label", "")
    locator = page.get_by_label(aria_label)
    if await locator.count() != 0:
        return locator.last

    name = attributes.get("name", "")
    locator = page.locator(f'[name="{name}"]')
    if await locator.count() != 0:
        return locator.last

    type = attributes.get("type", "")
    locator = page.locator(f'[type="{type}"]')
    if await locator.count() != 0:
        return locator.last

    class_list = attributes.get("classList", [])
    for class_l in class_list:
        locator = page.locator(f".{class_l}")
        if 0 < await locator.count() <= 1:
            return locator.last

    # placeholder = attributes.get("placeholder", "")
    # locator = self.page.get_by_placeholder(placeholder)
    # if await locator.count() != 0:
    #     return locator

    # role = attributes.get("role", "")
    # locator = self.page.get_by_role()

    return None
