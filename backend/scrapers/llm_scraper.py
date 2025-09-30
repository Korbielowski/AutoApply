from playwright.async_api import Locator, Page
from pydantic import ValidationError
from loguru import logger

from backend.scrapers.base_scraper import BaseScraper, JobEntry
from backend.scrapers.utils import (
    goto,
    click,
    fill,
    get_page_content,
    find_html_element,
    find_html_element_attributes,
)
from backend.llm import send_req_to_llm


# TODO: Add try except blocks to all operations that can timeout
# TODO: Save all important information about the pages in database (e.g. links, buttons, fields, scrollbars)
# for later use, so that we don't make so many requests to LLM if we already know certain page.
# If saved information does not work at any stage of the process, switch back to LLM scraper and update adequate steps in database
class LLMScraper(BaseScraper):
    async def login_to_page(self) -> None:
        await goto(self.page, self.link)
        # TODO: Make a loop out of this code
        await self._pass_cookies_popup()
        if not await self._is_on_login_page():
            await self._navigate_to_login_page()

        email_field_locator = await find_html_element(
            self.page, "Find the login input field for username/email."
        )
        password_field_locator = await find_html_element(
            self.page, "Find the login input field for password."
        )
        sign_in_btn_locator = await find_html_element(
            self.page, "Find the sign in/login button."
        )

        await fill(email_field_locator, self.email)
        await fill(password_field_locator, self.password)
        await click(sign_in_btn_locator, self.page)

    async def _is_on_login_page(self) -> bool:
        url = self.page.url
        if "login" in url or "signin" in url or "sign-in" in url or "sign_in" in url:
            return True

        if "True" in await send_req_to_llm(
            f"Determine if this site is a login page, return only True or False: {await get_page_content(self.page)}",
            use_openai=True,
        ):
            return True

        return False

    async def _navigate_to_login_page(self) -> None:
        btn = await find_html_element(self.page, "Find a button that opens login page")
        await click(btn, self.page)

    async def _pass_cookies_popup(self) -> None:
        # TODO: Try using cookies to avoid popups
        btn = await find_html_element(
            self.page, "Find button responsible for accepting website cookies"
        )
        await click(btn, self.page)

    # TODO: Change this method name to "_navigate_to_job_list"
    async def _go_to_job_list(self) -> None:
        btn = await find_html_element(self.page, "Find button that opens job list")
        await click(btn, self.page)

    async def get_job_entries(self) -> tuple[Locator, ...]:
        element = await find_html_element(
            self.page,
            "Find an element that is at the bottom of the page, so once in view port it loads all of the page content",
        )
        if not element:
            logger.exception(
                "Could not find an element that is at the bottom of the page"
            )
            return tuple()
        await element.scroll_into_view_if_needed()

        attributes = await find_html_element_attributes(
            self.page,
            "Find an element that is responsible for holding job entry information and link to job offer. CSS class that are to be selected, must only select job entries and no other elements",
        )
        if not attributes:
            logger.exception(
                "Cannot find attributes that would enable scraper to find job entries"
            )
            return tuple()

        logger.info(f"{attributes=}")
        class_list = attributes.get("classList", [])
        for class_l in class_list:
            locator = self.page.locator(f".{class_l}")
            response = await send_req_to_llm(
                f"Does this CSS class '{class_l}' select only job offers and no other elements. Return 'True' if only jobs are selected and 'False' if '{class_l}' class selects also other elements. {'\n'.join(await locator.all_inner_texts())}",
                use_openai=True,
            )
            if "True" in response:
                logger.info(
                    f"Chosen {class_l} as it only selects job entries on the page"
                )
                logger.info(
                    f"Amount of elements selected by {class_l} CSS class: {len(await locator.all())}"
                )
                return tuple(await locator.all())
        return tuple()

    async def go_to_next_page(self) -> bool:
        btn = await find_html_element(
            self.page,
            "Find button that is responsible for moving to next job listing page",
        )
        if not btn:
            logger.info("Could not find next page button")
            return False
        await click(btn, self.page)
        return True

    async def _go_to_next_job(self) -> bool:
        pass

    async def _apply_for_job(self):
        pass

    async def _get_job_information(self, link: str) -> None | JobEntry:
        job_page: Page = await self.browser.new_page(locale="en-US")
        await goto(job_page, link)

        response = await send_req_to_llm(
            f"Get job information like title, company_name, requirements, duties, about_project, offer_benefits, location, contract_type, employment_type, work_arrangement, additional_information. Do not explain, only return JSON\n{await get_page_content(job_page)}",
            use_openai=True,
        )
        await job_page.close()

        try:
            return JobEntry.model_validate_json(response)
        except ValidationError as e:
            logger.exception(e)
        return None
