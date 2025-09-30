# TODO: If not used, remove openai-agents from dependencies and add normal OpenAI
# TODO: Remove dotenv and code related to it from this file, when app setup works fine
from openai import OpenAI, RateLimitError, AuthenticationError
from dotenv import load_dotenv
from loguru import logger

import os
import asyncio

# TODO: Uncomment this in the future: from app_setup import API_KEY
load_dotenv()
API_KEY = os.getenv("API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = "https://api.llm7.io/v1"
MODEL = "deepseek-r1-0528"
OPENAI_MODEL = "gpt-5-nano-2025-08-07"


async def send_req_to_llm(
    prompt: str, temperature: float = 1, use_openai: bool = False, retry: int = 3
) -> str:
    # response = LLM.responses.create(model="deepseek/deepseek-r1-distill-llama-70b:free", instructions=prompt, input=str(description))
    response = ""

    if use_openai:
        client = OpenAI(api_key=OPENAI_API_KEY)
        while not response and retry > 0:
            try:
                response = client.responses.create(
                    model=OPENAI_MODEL, input=prompt, temperature=temperature
                )
            except RateLimitError as e:
                logger.info(f"LLM error: {e}")
                logger.error("Too many tokens in 1 minute")
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

                logger.info(f"Sleeping for: {delay} seconds")
                await asyncio.sleep(delay)
            except AuthenticationError as e:
                logger.info(f"LLM error: {e}")
            retry -= 1

            return response.output_text
    else:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
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
