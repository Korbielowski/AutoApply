from playwright_stealth import Stealth
from playwright.async_api import async_playwright
import pytest
from loguru import logger

from backend.scrapers import LLMScraper
from backend.models import ProfileModel

import logging


@pytest.mark.asyncio
@pytest.mark.skip
async def test_is_on_login_page_return_false_when_not_on_login_page(
    get_data_for_scraper,
):
    async with Stealth().use_async(async_playwright()) as playwright:
        playwright.selectors.set_test_id_attribute("data-control-id")
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page(locale="en-US")
        profile, email, password = get_data_for_scraper
        link = "https://pracuj.pl/"
        scraper = LLMScraper(
            link=link,
            profile=profile,
            email=email,
            password=password,
            page=page,
            auto_apply=False,
            generate_cv=False,
        )
        await scraper.page.goto(scraper.link)
        await scraper.page.wait_for_load_state("load")
        assert await scraper._is_on_login_page() is False


@pytest.mark.asyncio
@pytest.mark.skip
async def test_is_on_login_page_return_true_when_on_login_page(
    get_data_for_scraper,
):
    async with Stealth().use_async(async_playwright()) as playwright:
        playwright.selectors.set_test_id_attribute("data-control-id")
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page(locale="en-US")
        profile, email, password = get_data_for_scraper
        link = "https://login.pracuj.pl/"
        scraper = LLMScraper(
            link=link,
            profile=profile,
            email=email,
            password=password,
            page=page,
            auto_apply=False,
            generate_cv=False,
        )
        await scraper.page.goto(scraper.link)
        await scraper.page.wait_for_load_state("load")
        assert await scraper._is_on_login_page() is True


@pytest.mark.asyncio
@pytest.mark.skip
async def test_navigate_to_login_page(get_data_for_scraper, caplog):
    async with Stealth().use_async(async_playwright()) as playwright:
        playwright.selectors.set_test_id_attribute("data-control-id")
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page(locale="en-US")
        profile, email, password = get_data_for_scraper
        link = "https://pracuj.pl/"
        scraper = LLMScraper(
            link=link,
            profile=profile,
            email=email,
            password=password,
            page=page,
            auto_apply=False,
            generate_cv=False,
        )
        await scraper.page.goto(scraper.link)
        await scraper.page.wait_for_load_state("load")
        with caplog.at_level(logging.ERROR):
            await scraper._navigate_to_login_page()
            assert "Could not find button to login page" not in caplog.text


@pytest.mark.asyncio
@pytest.mark.skip
async def test_loging_to_page(get_data_for_scraper, caplog):
    async with Stealth().use_async(async_playwright()) as playwright:
        playwright.selectors.set_test_id_attribute("data-control-id")
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page(locale="en-US")
        profile, email, password = get_data_for_scraper
        link = "https://pracuj.pl/"
        scraper = LLMScraper(
            link=link,
            profile=profile,
            email=email,
            password=password,
            page=page,
            auto_apply=False,
            generate_cv=False,
        )
        with caplog.at_level(logging.ERROR):
            await scraper.login_to_page()
            assert "Could not log into" not in caplog.text


@pytest.mark.asyncio
@pytest.mark.skip
async def test_get_page_content(get_data_for_scraper, caplog):
    async with Stealth().use_async(async_playwright()) as playwright:
        playwright.selectors.set_test_id_attribute("data-control-id")
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page(locale="en-US")
        profile, email, password = get_data_for_scraper
        link = "https://pracuj.pl/"
        scraper = LLMScraper(
            link=link,
            profile=profile,
            email=email,
            password=password,
            page=page,
            auto_apply=False,
            generate_cv=False,
        )
        await scraper.page.goto(scraper.link)
        await scraper.page.wait_for_load_state("load")
        content = await scraper._get_page_content()
        logger.info(type(content))
        assert type(content) is not str


@pytest.mark.asyncio
async def test_get_job_entries(get_data_for_scraper):
    async with Stealth().use_async(async_playwright()) as playwright:
        playwright.selectors.set_test_id_attribute("data-control-id")
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page(locale="en-US")
        profile, email, password = get_data_for_scraper
        link = "https://it.pracuj.pl/praca"
        scraper = LLMScraper(
            link=link,
            profile=profile,
            email=email,
            password=password,
            page=page,
            auto_apply=False,
            generate_cv=False,
        )
        await scraper.page.goto(scraper.link)
        await scraper.page.wait_for_load_state("load")
        await scraper._pass_cookies_popup()
        job_entries = await scraper.get_job_entires()
        logger.info(f"Amount of jobs from page: {len(job_entries)}")
        for job in job_entries:
            logger.info(await job.all_text_contents())
        assert type(job_entries) is tuple
        assert len(job_entries) > 0


@pytest.fixture(
    scope="module",
)
def get_data_for_scraper() -> tuple[ProfileModel, str, str]:
    profile = ProfileModel(
        firstname="test", middlename="test", surname="test", age="30"
    )
    email = "test.test@gmail.com"
    password = "testTest123"
    return profile, email, password
