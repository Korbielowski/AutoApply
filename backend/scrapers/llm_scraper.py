from playwright.async_api import Locator
from loguru import logger

from .base_scraper import BaseScraper, JobEntry
from ..llm import send_req_to_llm

import json


class LLMScraper(BaseScraper):
    async def login_to_page(self) -> None:
        await self.page.goto(self.link)
        await self.page.wait_for_load_state("load")

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

        await email_field_locator.fill(self.email)
        await password_field_locator.fill(self.password)
        await sign_in_btn_locator.click()
        await self.page.wait_for_load_state("load")

    async def _go_to_job_list(self) -> None:
        pass

    async def get_job_entires(self) -> tuple[Locator, ...]:
        pass

    async def go_to_next_page(self) -> bool:
        pass

    async def _go_to_next_job(self) -> bool:
        pass

    async def _apply_for_job(self):
        pass

    async def _get_job_information(self, retry: int = 3) -> None | JobEntry:
        pass

    async def find_html_element(self, prompt: str) -> None | Locator:
        pre_prompt = "I will give you an HTML snippet."
        post_prompt = "Return only its identifying attributes in JSON format with the following keys: id, name, type, aria-label, placeholder, role, text, classList. If an attribute does not exist, return null for it. Do not explain, only return JSON"
        page_content = (
            await self.page.content()
        )  # TODO: Make page content smaller by e.g. excluding head or code tags
        response = send_req_to_llm(f"{pre_prompt}{prompt}{post_prompt}\n{page_content}")

        try:
            attributes = json.loads(response)
            logger.info(f"List of attributes:\n{json.dumps(attributes, indent=2)}")
        except json.JSONDecodeError as e:
            logger.exception(e)
            return None

        id = attributes.get("id", "")
        locator = self.page.locator(f"#{id}")
        if locator.count() != 0:
            return locator

        name = attributes.get("name", "")
        locator = self.page.locator(f'[name="{name}"]')
        if locator.count() != 0:
            return locator

        type = attributes.get("type", "")
        locator = self.page.locator(f'[type="{type}"]')
        if locator.count() != 0:
            return locator

        aria_label = attributes.get("aria-label", "")
        locator = self.page.get_by_label(aria_label)
        if locator.count() != 0:
            return locator

        placeholder = attributes.get("placeholder", "")
        locator = self.page.get_by_placeholder(placeholder)
        if locator.count() != 0:
            return locator

        text = attributes.get("text", "")
        locator = self.page.get_by_text(text)
        if locator.count() != 0:
            return locator

        # class_list = attributes.get("classList", "")
        # locator = self.page.get_by()

        # role = attributes.get("role", "")
        # locator = self.page.get_by_role()

        return None
