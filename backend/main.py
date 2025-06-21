from .app_setup import app, templates
from .models import ProfileInfoModel
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse


@app.get("/")
# @authenticate_user
async def root(request: Request):
    print("Elo")
    return RedirectResponse(url=request.url_for("create_user"))
    # return templates.TemplateResponse(request=request, name="index.html")


@app.get("/create_user")
async def load_user_form(request: Request):
    return templates.TemplateResponse(request=request, name="create_user.html")


@app.post("/create_user/")
async def create_user(form_data: ProfileInfoModel):  # form: Annotated[TestInfo, Form()]
    print(form_data)
    # with Session(app_setup.engine) as session:
    #     info_validated = (
    #         i.__class__.model_validate(i) for i in profile_information.model_dump()
    #     )
    # session.add_all(info_validated)
    # session.commit()
    # session.refresh()
    # return RedirectResponse(url=app.url_path_for("test"))


@app.post("/test")
async def test(request: Request):
    return HTMLResponse("<h1>Hello</h1>")
