from functools import lru_cache

import aiofiles
import yaml


# TODO: Make this function fully async
@lru_cache()
async def load_prompt(prompt_path: str, **kwargs) -> str:
    paths = prompt_path.split(":")
    if len(paths) < 2:
        raise Exception(
            "prompt_path parameter should be specified as this 'example:example'"
        )

    data: dict = {}
    async with aiofiles.open(paths[0], "r") as file:
        file_content = await file.read()
        data = yaml.safe_load(file_content)
        if type(data) is not dict:
            raise Exception(f"Bad yaml structure in this file: {paths[0]}")

    for p in paths[1:]:
        data = data.get(p, {})

    prompt = data.get("prompt", "")
    params = data.get("params", [])

    if kwargs and params:
        prompt = prompt.format_map(**kwargs)
    return prompt
