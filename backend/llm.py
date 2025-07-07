from openai import OpenAI


from app_setup import API_KEY

LLM = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)
MODEL = "deepseek/deepseek-r1-distill-llama-70b:free"


def send_req_to_llm(prompt: str) -> str:
    # response = LLM.responses.create(model="deepseek/deepseek-r1-distill-llama-70b:free", instructions=prompt, input=str(description))
    # logging.info(f"Response from LLM: {response}")
    try:
        completion = LLM.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"LLM error: {e}")
    return ""
