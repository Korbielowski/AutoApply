from playwright.async_api import Page, Locator
from pydantic import BaseModel
from loguru import logger

from pathlib import Path
import json
import abc
import os

from ..llm import send_req_to_llm
from ..models import ProfileModel
from ..pdf import create_cv


class JobEntry(BaseModel):
    posting_id: int
    description: str
    location: str
    company_url: str


class BaseScraper(abc.ABC):
    def __init__(
        self,
        link: str,
        profile: ProfileModel,
        email: str,
        password: str,
        page: Page,
        auto_apply: bool = False,
        generate_cv: bool = False,
    ) -> None:
        self.link = link
        self.profile = ProfileModel
        self.email = email
        self.password = password
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
    async def _go_to_next_page(self) -> bool:
        pass

    @abc.abstractmethod
    async def _go_to_next_job(self) -> bool:
        pass

    @abc.abstractmethod
    async def _apply_for_job(self):
        pass

    @abc.abstractmethod
    async def _get_job_information(self, retry: int = 3) -> JobEntry:
        pass

    async def process_job(self, locator: Locator = None) -> str:
        job_entry = self._get_job_information(locator)

        # TODO: Evaluate job entry based on comparison between job's description and user's skills
        is_valuable, requirements = self._evaluate_job(job_entry.description)

        if is_valuable:
            logger.info("You should apply")
            # TODO: Add use_own_cv flag to options
            use_own_cv = False
            if not use_own_cv:
                cv = create_cv(
                    self.profile,
                    job_entry.posting_id,
                    requirements,
                    job_entry.location,
                    job_entry.company_url,
                    "llm-selection",
                )
            else:
                path = os.getenv("USER_CV", "")
                if not path:
                    logger.error("USER_CV variable with path to user's cv is not set")
                    return
                cv = Path(path)
                logger.info(cv)
            # _apply_for_job(page, cv)
        else:
            logger.info("You should not apply")
        return json.dumps(
            {
                "posting_id": job_entry.posting_id,
                "description": job_entry.description,
                "location": job_entry.location,
                "company_url": job_entry.company_url,
            }
        )

    async def _evaluate_job(self, description: str) -> tuple[bool, str]:
        # TODO: Make LLM compare user's skills with skills in the description
        prompt = f"Get only skills, qualifications, place required for this role from the description and return only them in your response and nothing more. {str(description)}"
        requirements = send_req_to_llm(prompt, temperature=0)
        logger.info(f"Important information about the posiotion: {requirements}")
        user_needs = "C, Rust, Poland, Python 5+ years, CI/CD, GIT, python testing, fluent polish"
        prompt = f"Compare my qualifications and needs: {user_needs}. With these from job offer: {requirements}. Return only one word, True if I should apply, and False if not and no other words/characters"
        response = send_req_to_llm(prompt + str(description), temperature=0)
        logger.info(f"LLM evalutaion: {response}")
        if "True" in response:
            return (True, requirements)
        else:
            return (False, requirements)
