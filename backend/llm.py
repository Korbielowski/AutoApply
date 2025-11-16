# TODO: If not used, remove openai-agents from dependencies and add normal OpenAI
# TODO: Remove dotenv and code related to it from this file, when app setup works fine
import asyncio

from openai import AuthenticationError, OpenAI, RateLimitError
from sqlmodel import SQLModel

from backend.config import settings
from backend.logging import get_logger

BASE_URL = "https://api.llm7.io/v1"
MODEL = "deepseek-r1-0528"
# OPENAI_MODEL = "gpt-5-nano-2025-08-07"
OPENAI_MODEL = "gpt-5-mini-2025-08-07"
logger = get_logger()


async def send_req_to_llm(
    prompt: str,
    temperature: float = 1,
    use_openai: bool = True,
    use_json_schema: bool = False,
    model: SQLModel | None = None,
    retry: int = 3,
) -> str:
    # response = LLM.responses.create(model="deepseek/deepseek-r1-distill-llama-70b:free", instructions=prompt, input=str(description))
    response = ""

    if use_openai:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        while not response and retry > 0:
            try:
                if use_json_schema and model:
                    response = client.responses.parse(
                        model=OPENAI_MODEL,
                        input=prompt,
                        temperature=temperature,
                        text_format=model,
                    )
                    if response.output_parsed:
                        return response.output_parsed
                else:
                    response = client.responses.create(
                        model=OPENAI_MODEL,
                        input=prompt,
                        temperature=temperature,
                    )
                    if response:
                        return response.output_text
            except RateLimitError as e:
                logger.info(f"LLM error: {e}")
                logger.error("Too many tokens in 1 minute")
                logger.error(f"Response headers: {e.response.headers}")
                # time = (
                #     e.response.headers.get("x-ratelimit-reset-tokens", "")
                #     .replace("m", "m ")
                #     .replace("s", "")
                #     .split(" ")
                # )
                # delay = 0
                #
                # if "m" in time[0]:
                #     delay += int(time.replace("m", "")) * 60
                # # ERROR: Crashes when time is empty string
                # delay += int(time[-1])
                #
                # logger.info(f"Sleeping for: {delay} seconds")
                delay = 10
                await asyncio.sleep(delay)
            except AuthenticationError as e:
                logger.info(f"LLM error: {e}")
            retry -= 1
    else:
        client = OpenAI(api_key=settings.API_KEY, base_url=BASE_URL)
        try:
            response = client.responses.create(
                model=MODEL,
                input=prompt,
                # messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )
            return response.output_text
        except Exception as e:
            logger.info(f"LLM error: {e}")
    return ""
