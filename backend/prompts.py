from functools import lru_cache

import aiofiles
import yaml
from pydantic import BaseModel

from backend.config import settings


# TODO: Make this function fully async
@lru_cache()
async def load_prompt(
    prompt_path: str, model: BaseModel | None = None, **kwargs
) -> str:
    paths = prompt_path.split(":")
    if len(paths) < 2:
        raise Exception(
            "prompt_path parameter should be specified as this 'example:example'"
        )

    data: dict = {}
    prompt_file_path = settings.ROOT_DIR / "prompts" / f"{paths[0]}.yaml"
    async with aiofiles.open(prompt_file_path, "r") as file:
        file_content = await file.read()
        data = yaml.safe_load(file_content)
        if type(data) is not dict:
            raise Exception(f"Bad yaml structure in this file: {paths[0]}")

    for p in paths[1:]:
        data = data.get(p, {})

    prompt = data.get("prompt", "")
    params = data.get("params", [])

    if not prompt:
        raise Exception(
            f"Some error occurred while retrieving 'prompt' key from {prompt_file_path} and specified prompt path: {prompt_path}"
        )

    if params:
        if model:
            kwargs.update(model.model_dump())
        try:
            prompt = prompt.format_map(kwargs)
        except KeyError as e:
            raise Exception(f"Keyword argument/s missing: {e.args}")
    return prompt
