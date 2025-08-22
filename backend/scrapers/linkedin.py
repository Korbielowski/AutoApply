from playwright.async_api import Locator
from loguru import logger

import json
import re

from .base_scraper import BaseScraper, JobEntry


class LinkedIn(BaseScraper):
    async def login_to_page(self) -> None:
        # TODO: Add functionality to check whether we got verification code on email or not
        # TODO: Add ability to log into many pages using LLM
        await self.page.goto(self.link)
        await self.page.wait_for_load_state("load")
        await self.page.get_by_label("Email or phone").fill(self.email)
        await self.page.get_by_label("Password").fill(self.password)
        await self.page.get_by_label("Sign in").last.click()
        await self.page.wait_for_load_state("load")

    async def _go_to_job_list(self) -> None:
        pass

    async def get_job_entires(self) -> tuple[Locator, ...]:
        pattern = re.compile(r".*")
        ld: dict = {}  # TODO: Check if set would be faster than dict
        max_scrolls = 20
        wheel_move = 200
        start_pos_x = (
            int(
                await self.page.evaluate(
                    "Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0)"
                )
            )
            / 3
        )
        start_pos_y = int(
            await self.page.evaluate(
                "Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0)"
            )
            / 2
        )

        await self.page.mouse.move(start_pos_x, start_pos_y)

        # TODO: Find a better way for scrolling through the whole page (https://scrapfly.io/blog/answers/how-to-scroll-to-the-bottom-with-playwright)
        for _ in range(max_scrolls):
            locator = self.page.get_by_test_id(pattern)
            for i in range(await locator.count()):
                a_tag = locator.nth(i)
                href = await a_tag.get_attribute("href")
                if href not in ld:
                    ld[href] = a_tag
            await self.page.mouse.wheel(0, wheel_move)
            await self.page.wait_for_timeout(500)
        return tuple(ld.values())

    async def go_to_next_page(self) -> bool:
        try:
            await self.page.get_by_label("View next page").last.click()
        except TimeoutError:
            logger.error("Timeout :(")
            return False
        return True

    async def _go_to_next_job(self) -> bool:
        # if :
        #     if not _go_to_next_page(page):
        #         return False
        pass

    async def _apply_for_job(self):
        pass

    async def _get_job_information(self, retry: int = 3) -> None | JobEntry:
        data = None

        # TODO: Make this loop make more sense, by maybe doing something more
        while data is None:
            if retry <= 0:
                logger.error("Cannot get information about job entry")
                break
            page_content = await self.page.content()
            data = re.search(r"{\"data\":{\"dashEntityUrn\":.*}", page_content)
            retry -= 1

        if data is None:
            logger.error("Did not get information about the job entry")
            return None

        job_data = json.loads(data.group())
        posting_id = int(job_data["data"]["jobPostingId"])
        logger.info(f"job posting id: {posting_id}")
        # TODO: Check if job id is already in database, if so, go to next job entry
        # with Session(engine) as session:
        #     hashed_id = hash(posting_id)
        #     stmt = select(JobEntry).where(JobEntry.posting_id == hashed_id)
        #     result = session.exec(stmt)
        #     if result:
        #         logger.error("Job posting is already in database")

        description = job_data.get("data", {}).get("description", {}).get("text", "")
        location = job_data.get("data", {}).get("formattedLocation", "")
        company_url = (
            job_data.get("data", {}).get("applyMethod", {}).get("companyApplyUrl", "")
        )
        return JobEntry(
            posting_id=posting_id,
            description=description,
            location=location,
            company_url=company_url,
        )
