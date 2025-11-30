import abc

from playwright.async_api import BrowserContext, Locator, Page

from backend.database.models import JobEntry, WebsiteModel
from backend.llm.llm import send_req_to_llm
from backend.logging import get_logger

logger = get_logger()


class BaseScraper(abc.ABC):
    def __init__(
        self,
        url: str,
        email: str,
        password: str,
        context: BrowserContext,
        page: Page,
        website_info: WebsiteModel | None,
    ) -> None:
        self.url = url
        self.email = (
            email  # TODO: Get email for each website separately from database
        )
        self.password = password  # TODO: Get password for each website separately from database
        self.context = context
        self.page = page
        self.website_info = website_info if website_info else WebsiteModel()

    @abc.abstractmethod
    async def login_to_page(self) -> None:
        pass

    @abc.abstractmethod
    async def _navigate_to_job_list_page(self) -> None:
        pass

    @abc.abstractmethod
    async def get_job_entries(self) -> tuple[Locator, ...]:
        pass

    @abc.abstractmethod
    async def navigate_to_next_page(self) -> bool:
        pass

    @abc.abstractmethod
    async def _go_to_next_job(self) -> bool:
        pass

    @abc.abstractmethod
    async def _apply_for_job(self):
        pass

    @abc.abstractmethod
    async def _get_job_information(self, url: str) -> JobEntry | None:
        pass

    async def process_and_evaluate_job(
        self, locator: Locator
    ) -> JobEntry | None:
        url_2 = await locator.get_attribute("href")
        url = await locator.get_attribute(
            "href"
        )  # FIXME: This does not return url as this locator is more general and is a parent for other elements, also for a tag with url to job offer
        logger.info(
            f"Url with get_by_role: {url_2}\nUrl with get_attribute: {url}"
        )
        job_entry = await self._get_job_information(url_2)

        if not job_entry:
            logger.error(f"job_entry: {job_entry}")
            return None

        logger.info(f"job_entry: {job_entry.model_dump_json()}")

        # TODO: Get user needs
        user_needs = ""
        prompt = f"Compare user qualifications and needs: {user_needs}. With these from job offer: {job_entry.model_dump_json()}. Return only one word, True if I should apply, and False if not and no other words/characters"
        response = await send_req_to_llm(prompt, use_openai=True)
        logger.info(f"LLM evaluation: {response}")

        if "True" in response:
            return job_entry
        else:
            return None
