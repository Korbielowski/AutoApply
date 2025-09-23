from playwright.async_api import Browser, Page, Locator
from pydantic import BaseModel
from loguru import logger

import abc
from datetime import date

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
        auto_apply: bool = False,
        generate_cv: bool = False,
    ) -> None:
        self.link = link
        self.profile = ProfileModel
        self.email = email
        self.password = password
        self.browser = browser
        self.page = page
        self.auto_apply = auto_apply
        self.generate_cv = generate_cv

    @abc.abstractmethod
    async def login_to_page(self) -> None:
        pass

    @abc.abstractmethod
    async def _go_to_job_list(self) -> None:
        pass

    @abc.abstractmethod
    async def get_job_entires(self) -> tuple[Locator, ...]:
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
    async def _get_job_information(self, retry: int = 3) -> None | JobEntry:
        pass

    async def process_job(self, locator: Locator) -> str:
        await locator.highlight()
        await locator.first.click()
        await self.page.wait_for_selector(".jobs-description__content")
        # logger.info(f"{self.page.url}\n{await locator.inner_text()}\n\n")
        job_entry = await self._get_job_information()
        if not job_entry:
            return ""

        logger.info(job_entry.json())
        # TODO: Evaluate job entry based on comparison between job's description and user's skills
        # is_valuable, requirements = self._evaluate_job(job_entry.description)

        # if is_valuable:
        #     logger.info("You should apply")
        #     # TODO: Add use_own_cv flag to options
        #     use_own_cv = False
        #     if not use_own_cv:
        #         cv = create_cv(
        #             self.profile,
        #             job_entry.posting_id,
        #             requirements,
        #             job_entry.location,
        #             job_entry.company_url,
        #             "llm-selection",
        #         )
        #     else:
        #         path = os.getenv("USER_CV", "")
        #         if not path:
        #             logger.error("USER_CV variable with path to user's cv is not set")
        #             # TODO: Do not return information if job is not valuable
        #             return ""
        #         cv = Path(path)
        #         logger.info(cv)
        #     # _apply_for_job(page, cv)
        # else:
        #     logger.info("You should not apply")
        return job_entry.json()

    async def _evaluate_job(self, description: str) -> tuple[bool, str]:
        # TODO: Make LLM compare user's skills with skills in the description
        prompt = f"Get only skills, qualifications, place required for this role from the description and return only them in your response and nothing more. {str(description)}"
        requirements = await send_req_to_llm(prompt, temperature=0, use_openai=True)
        logger.info(f"Important information about the posiotion: {requirements}")
        user_needs = "C, Rust, Poland, Python 5+ years, CI/CD, GIT, python testing, fluent polish"
        prompt = f"Compare my qualifications and needs: {user_needs}. With these from job offer: {requirements}. Return only one word, True if I should apply, and False if not and no other words/characters"
        response = await send_req_to_llm(
            prompt + str(description), temperature=0, use_openai=True
        )
        logger.info(f"LLM evalutaion: {response}")
        if "True" in response:
            return (True, requirements)
        else:
            return (False, requirements)
