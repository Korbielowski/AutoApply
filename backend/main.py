from app_setup import app, templates
from fastapi import Request
from fastapi.responses import HTMLResponse


@app.get("/", response_class=HTMLResponse)
# @authenticate_user
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
