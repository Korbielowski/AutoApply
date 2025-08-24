# TODO: If not used, remove openaia-agents from dependencies and add normal OpenAI
# TODO: Remove dotenv and code related to it from this file, when app setup works fine
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger

import os

# TODO: Uncomment this in the future: from app_setup import API_KEY
load_dotenv()
API_KEY = os.getenv("API_KEY", "")
LLM = OpenAI(base_url="https://api.llm7.io/v1", api_key="unused")
MODEL = "deepseek-r1-0528"


def send_req_to_llm(prompt: str, temperature: float = 1) -> str:
    # response = LLM.responses.create(model="deepseek/deepseek-r1-distill-llama-70b:free", instructions=prompt, input=str(description))
    try:
        completion = LLM.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.info(f"LLM error: {e}")
    return ""
