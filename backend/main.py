from app_setup import app, templates
from fastapi import Request
from fastapi.responses import HTMLResponse

# from utils import authenticate_user


@app.get("/", response_class=HTMLResponse)
# @authenticate_user
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
