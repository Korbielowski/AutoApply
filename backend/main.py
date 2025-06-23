from .app_setup import app, templates
from .models import ProfileInfoModel
from fastapi import Request, status
from fastapi.responses import RedirectResponse


@app.get("/")
# @authenticate_user
async def root(request: Request):
    return RedirectResponse(url=request.url_for("load_user_form"))
    # return templates.TemplateResponse(request=request, name="index.html")


@app.get("/create_user")
async def load_user_form(request: Request):
    return templates.TemplateResponse(request=request, name="create_user.html")


@app.post("/create_user")
async def create_user(
    request: Request, form_data: ProfileInfoModel
):  # form: Annotated[TestInfo, Form()]
    print(form_data)
    # with Session(app_setup.engine) as session:
    #     info_validated = (
    #         i.__class__.model_validate(i) for i in profile_information.model_dump()
    #     )
    #     session.add_all(info_validated)
    #     session.commit()
    #     session.refresh()
    return RedirectResponse(
        url=request.url_for("test"), status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/test")
async def test(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
