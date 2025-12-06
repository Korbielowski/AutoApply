from pydantic import BaseModel


class HTMLElement(BaseModel):
    id: str = ""
    name: str = ""
    element_type: str = ""
    aria_label: str = ""
    placeholder: str = ""
    role: str = ""
    text: str = ""
    class_list: list[str] = []


class CVOutput(BaseModel):
    html: str
    css: str
