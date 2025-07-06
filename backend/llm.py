from dotenv import load_dotenv
from openai import OpenAI

import os

load_dotenv()
LLM = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("API_KEY", ""))
MODEL = "deepseek/deepseek-r1-distill-llama-70b:free"


def send_req_to_llm(prompt: str) -> str:
    try:
        completion = LLM.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"LLM error: {e}")
    return ""
