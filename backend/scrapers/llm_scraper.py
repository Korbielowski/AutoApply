from playwright.async_api import Locator
from openai import RateLimitError
from bs4 import BeautifulSoup
from loguru import logger
import tiktoken

from backend.scrapers.base_scraper import BaseScraper, JobEntry
from backend.llm import send_req_to_llm

import json
import asyncio

TIK = tiktoken.encoding_for_model("gpt-5-")


# TODO: Save all important information about the pages in database (e.g. links, buttons, fields, scrollbars)
# for later use, so that we don't make so many requests to LLM if we already know certain page.
# If saved information does not work at any stage of the process, switch back to LLM scraper and update adequate steps in database
class LLMScraper(BaseScraper):
    async def login_to_page(self) -> None:
        await self.page.goto(self.link)
        await self.page.wait_for_load_state("load")
        # TODO: Make a loop out of this code
        await self._pass_cookies_popup()
        if not await self._is_on_login_page():
            await self._navigate_to_login_page()

        email_field_locator = await self.find_html_element(
            "Find the login input field for username/email."
        )
        password_field_locator = await self.find_html_element(
            "Find the login input field for password."
        )
        sign_in_btn_locator = await self.find_html_element(
            "Find the sign in/login button."
        )

        if (
            not email_field_locator
            or not password_field_locator
            or not sign_in_btn_locator
        ):
            logger.error(
                f"Could not log into the site {self.link}, {email_field_locator=}, {password_field_locator=}, {sign_in_btn_locator=}"
            )
            return

        logger.info(
            f"{self.link}, {email_field_locator=}, {password_field_locator=}, {sign_in_btn_locator=}"
        )
        await email_field_locator.fill(self.email)
        await password_field_locator.fill(self.password)
        await sign_in_btn_locator.click()
        await self.page.wait_for_load_state("load")
        # await asyncio.sleep(10)

    async def _is_on_login_page(self) -> bool:
        url = self.page.url
        if "login" in url or "signin" in url or "sign-in" in url or "sign_in" in url:
            return True

        if "True" in send_req_to_llm(
            f"Determine if this site is a login page, return only True or False: {await self._get_page_content()}",
            use_openai=True,
        ):
            return True

        return False

    async def _navigate_to_login_page(self) -> None:
        btn = await self.find_html_element("Find a button that opens login page")
        if not btn:
            logger.error("Could not find button to login page")
            return
        logger.info(f"Found login button: {btn}\n{await btn.all_inner_texts()}")
        await btn.click()
        await self.page.wait_for_load_state("load")

    async def _pass_cookies_popup(self) -> None:
        # TODO: Try using cookies to avoid popups
        btn = await self.find_html_element(
            "Find button responsible for accepting website cookies"
        )
        if not btn:
            logger.error("Could not find cookies button")
            return
        logger.info(f"Found cookies button: {btn}\n{await btn.all_inner_texts()}")
        await btn.click()
        await self.page.wait_for_load_state("load")

    # TODO: Change this method name to "_navigate_to_job_list"
    async def _go_to_job_list(self) -> None:
        btn = await self.find_html_element("Find button that opens job list")
        if not btn:
            logger.error("Could not find job list button")
            return
        logger.info(f"Found job list button: {btn}\n{await btn.all_inner_texts()}")
        await btn.click()
        await self.page.wait_for_load_state("load")

    async def get_job_entires(self) -> tuple[Locator, ...]:
        element = await self.find_html_element(
            "Find an element that is at the bottom of the page, so once in view port it loads all of the page content"
        )
        if not element:
            logger.error("Could not find job list button")
            return tuple()
        await element.scroll_into_view_if_needed()

        attributes = await self.find_html_element_attributes(
            "Find an element that is responsible for holding job entry information and link to job offer"
        )
        if not attributes:
            logger.error(
                "Cannot find attributes that would enable scraper to find job entries"
            )
            return tuple()

        class_list = attributes.get("classList", "").split(" ")
        for class_l in class_list:
            locator = self.page.locator(f".{class_l}")
            if await locator.count() == 0:
                continue
            return tuple(await locator.all())
        return tuple()

    async def go_to_next_page(self) -> bool:
        pass

    async def _go_to_next_job(self) -> bool:
        pass

    async def _apply_for_job(self):
        pass

    async def _get_job_information(self, retry: int = 3) -> None | JobEntry:
        pass

    async def find_html_element(self, prompt: str) -> None | Locator:
        attributes = await self.find_html_element_attributes(prompt)
        if not attributes:
            return None

        # TODO: Make sure that we are selecting only one element, especially true for "type" and "classList"
        id = attributes.get("id", "")
        locator = self.page.locator(f"#{id}")
        if await locator.count() != 0:
            return locator.last

        text = attributes.get("text", "")
        locator = self.page.get_by_text(text)
        if await locator.count() != 0:
            return locator.last

        aria_label = attributes.get("aria-label", "")
        locator = self.page.get_by_label(aria_label)
        if await locator.count() != 0:
            return locator.last

        name = attributes.get("name", "")
        locator = self.page.locator(f'[name="{name}"]')
        if await locator.count() != 0:
            return locator.last

        type = attributes.get("type", "")
        locator = self.page.locator(f'[type="{type}"]')
        if await locator.count() != 0:
            return locator.last

        # placeholder = attributes.get("placeholder", "")
        # locator = self.page.get_by_placeholder(placeholder)
        # if await locator.count() != 0:
        #     return locator

        # class_list = attributes.get("classList", "")
        # locator = self.page.get_by()

        # role = attributes.get("role", "")
        # locator = self.page.get_by_role()

        return None

    async def find_html_element_attributes(self, prompt: str) -> None | dict:
        pre_prompt = "I will give you an HTML snippet."
        post_prompt = "Return only its identifying attributes in JSON format with the following keys: id, name, type, aria-label, placeholder, role, text, classList. If an attribute does not exist, return null for it. Do not explain, only return JSON"
        page_content = await self._get_page_content()
        prompt = f"{pre_prompt}{prompt}{post_prompt}\n{page_content}"

        try:
            response = send_req_to_llm(
                prompt,
                use_openai=True,
            )
        except RateLimitError as e:
            time = (
                e.response.headers.get("x-ratelimit-reset-tokens", "")
                .replace("m", "m ")
                .replace("s", "")
                .split(" ")
            )
            delay = 0

            if "m" in time[0]:
                delay += int(time.replace("m", "")) * 60
            delay += int(time[-1])

            await asyncio.sleep(delay)
            response = send_req_to_llm(
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

    # TODO: Move this method to BaseScraper class as it can be also used in other derived classes
    async def _get_page_content(self) -> str:
        # TODO: Make page content smaller by e.g. excluding head or code tags and only by including body
        # TODO: Check in the future, whether regex would not be faster and overall better solution
        page_content = await self.page.content()
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
            logger.info(f"Amount of tokens: {len(TIK.encode(cleaned_page_content))}")
        return cleaned_page_content
