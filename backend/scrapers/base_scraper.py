import abc
from datetime import date

from loguru import logger
from playwright.async_api import Browser, Locator, Page
from pydantic import BaseModel

from backend.llm import send_req_to_llm
from backend.models import ProfileModel


# TODO: How to recognise duplicate job offers on a different sites and on the same site at different time
# Maybe try using normalization of several job information e.g. title, company name and part of description and fuzzy matching
# https://github.com/rapidfuzz/RapidFuzz
class JobEntry(BaseModel):
    title: str
    company_name: str
    discovery_date: date
    job_url: str
    requirements: str
    duties: str
    about_project: str
    offer_benefits: str
    location: str
    contract_type: str
    employment_type: str
    work_arrangement: str
    additional_information: None | str
    company_url: (
        None | str
    )  # TODO: Here LLM will need to find information on the internet


class BaseScraper(abc.ABC):
    def __init__(
        self,
        link: str,
        profile: ProfileModel,
        email: str,
        password: str,
        browser: Browser,
        page: Page,
    ) -> None:
        self.link = link
        self.profile = profile
        self.email = email
        self.password = password
        self.browser = browser
        self.page = page

    @abc.abstractmethod
    async def login_to_page(self) -> None:
        pass

    @abc.abstractmethod
    async def _go_to_job_list(self) -> None:
        pass

    @abc.abstractmethod
    async def get_job_entries(self) -> tuple[Locator, ...]:
        pass

    @abc.abstractmethod
    async def go_to_next_page(self) -> bool:
        pass

    @abc.abstractmethod
    async def _go_to_next_job(self) -> bool:
        pass

    @abc.abstractmethod
    async def _apply_for_job(self):
        pass

    @abc.abstractmethod
    async def _get_job_information(self, link: str) -> None | JobEntry:
        pass

    async def process_and_evaluate_job(self, locator: Locator) -> str:
        link = await locator.get_attribute(
            "href"
        )  # FIXME: This does not return link as this locator is more general and is a parent for other elements, also for a tag with url to job offer
        job_entry = await self._get_job_information(link)

        if not job_entry:
            return ""

        logger.info(job_entry.model_dump_json())

        # TODO: Get user needs
        user_needs = ""
        prompt = f"Compare user qualifications and needs: {user_needs}. With these from job offer: {job_entry.model_dump_json()}. Return only one word, True if I should apply, and False if not and no other words/characters"
        response = await send_req_to_llm(prompt, temperature=0, use_openai=True)
        logger.info(f"LLM evaluation: {response}")

        if "True" in response:
            return job_entry.model_dump_json()
        else:
            return ""
