# TODO: Two possbile backends, first one markdown + pdfkit, second one pypandoc
# import markdown
# import pdfkit
from sqlalchemy import URL
from sqlmodel import SQLModel, create_engine, Session, select
from dotenv import load_dotenv
import pypandoc

# from app_setup import engine
from llm import send_req_to_llm
from models import (
    Profile,
    ProgrammingLanguage,
    Language,
    Tool,
    Certificate,
    Charity,
    Education,
    Experience,
    Project,
    SocialPlatform,
)

import os
from pathlib import Path
import tempfile
import datetime


PDF_ENGINE = "tectonic"
CV_DIR_NAME = "cv"
# CV_FILE_NAME = "cv.pdf"
TEMPLATE = """

"""
DRIVERNAME = "postgresql+psycopg"


def _get_info_for_cv() -> dict[str:str]:
    load_dotenv()  # TODO: Path to .env is "../.env"
    username = os.environ.get("POSTGRE_USERNAME")
    password = os.environ.get("POSTGRE_PASSWORD")
    host = os.environ.get("POSTGRE_HOST")
    database = os.environ.get("POSTGRE_DATABASE")
    url_oject = URL.create(
        drivername=DRIVERNAME,
        username=username,
        password=password,
        host=host,
        database=database,
    )
    engine = create_engine(url_oject)  # TODO: Remove 'echo' parameter when releasing
    SQLModel.metadata.create_all(engine)
    model_classes = (
        Profile,
        ProgrammingLanguage,
        Language,
        Tool,
        Certificate,
        Charity,
        Education,
        Experience,
        Project,
        SocialPlatform,
    )
    with Session(engine) as session:
        return {c.__name__: session.execute(select(c)) for c in model_classes}


def _create_cv(
    posting_id: str,
    requirements: str,
    location: str,
    company_url: str,
    mode: str = "",
) -> Path:
    # TODO: Here we will get data from the database
    # TODO: Make LLM compare and choose skills etc. that fit the description and then add them to the template:
    # 1) Get and process LLM output to put it into the template
    # 2) Make LLM put adequate skills etc. into the template string
    # 3) Make LLM write the CV from the ground up DONE
    # 4) Make algorthm for putting relevant skills into CV without use of LLM
    if mode == "llm-selection":
        info = _get_info_for_cv()
        prompt = f"Select skills and other qualifications from information: {info} that match those of job requirements: {requirements}"
        response = send_req_to_llm(prompt)
        prompt = f"Create a cv in markdown, based upon these skills and qualifications: {response}"
        cv = send_req_to_llm(prompt)
    else:
        info = _get_info_for_cv()
        for k, v in info.items():
            for x in v:
                print(f"Value: {x}")
        cv = "halo"
        # cv = TEMPLATE.format(
        #     name=name,
        #     email=email,
        #     phone_number=phone_number,
        #     linkedin=linkedin,
        #     github=github,
        #     personal_website=personal_website,
        #     profile=profile,
        #     experience=experience,
        #     education=education,
        #     skills=skills,
        #     projects=projects,
        #     certificates=certificates,
        #     languages=languages,
        # )
        #
    # html = markdown.markdown(template)
    # pdfkit.from_string(css + html, "cv.pdf")

    # WARNING: When using pypandoc we have to save markdown to a file in order to use convert_file function, beacause
    # when using convert_string function, the behaviour and output are not that good as when using first method

    current_time = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    cv_file_name = f"{current_time}_{posting_id}.pdf"

    if not os.path.isdir(CV_DIR_NAME):
        os.mkdir(CV_DIR_NAME)

    with tempfile.NamedTemporaryFile("w+", delete=False) as content_file:
        # styling_file = tempfile.NamedTemporaryFile("w+")
        content_file.write(cv)
        content_file.seek(0)
        print(
            f"File name: {content_file.name}, content:\n{''.join(content_file.readlines())}"
        )
        content_file.seek(0)
        pypandoc.convert_file(
            content_file.name,
            to="pdf",
            format="md",
            extra_args=[f"--pdf-engine={PDF_ENGINE}"],
            outputfile=Path().joinpath(CV_DIR_NAME).joinpath(cv_file_name),
        )
        # pypandoc.convert_text(
        #     template,
        #     to="pdf",
        #     format="md",
        #     extra_args=[f"--pdf-engine={PDF_ENGINE}"],
        #     outputfile=Path().joinpath(CV_DIR_NAME).joinpath(CV_FILE_NAME),
        # )

    return Path().joinpath(CV_DIR_NAME).joinpath(cv_file_name)

    # TODO: Maybe use try and finally blocks with tmpfiles
    # finally:
    #     content_file.close()
    #     os.unlink(content_file.name)

    # os.remove(Path().joinpath(CV_DIR_NAME).joinpath(CV_FILE_NAME))


if __name__ == "__main__":
    _create_cv("123", "", "", "")
