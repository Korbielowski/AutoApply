import aiofiles
import yaml


# TODO: Make this fully async
async def load_prompt(prompt_path: str, **kwargs) -> str:
    paths = prompt_path.split(":")
    if len(paths) < 2:
        raise Exception(
            "prompt_path parameter should be specified as this 'example:example'"
        )

    async with aiofiles.open(paths[0], "r") as file:
        file_content = await file.read()
        data: dict = yaml.safe_load(file_content)
        if type(data) is not dict:
            raise Exception(f"Bad yaml structure in this file: {paths[0]}")

    prompt = data.get(paths[1], "")
    if kwargs:
        prompt = prompt.format_map(**kwargs)
    return prompt
