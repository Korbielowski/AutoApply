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

# TODO: Use HTML and CSS instead of markdown, try maybe latex
CSS = """
<style>
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    max-width: 850px;
    margin: auto;
    padding: 20px;
    line-height: 1.6;
    color: #333;
  }
  h1 {
    border-bottom: 3px solid #555;
    padding-bottom: 5px;
    margin-bottom: 20px;
  }
  h2 {
    color: #00539C;
    margin-top: 40px;
    border-bottom: 1px solid #ccc;
    padding-bottom: 5px;
  }
  ul {
    margin-top: 0;
  }
  .contact {
    font-size: 0.95em;
    margin-bottom: 30px;
    color: #555;
  }
  .contact a {
    color: #00539C;
    text-decoration: none;
  }
  .section {
    margin-bottom: 30px;
  }
  .job-title {
    font-weight: bold;
    color: #222;
  }
  .job-company {
    font-style: italic;
    color: #666;
  }
  .job-dates {
    float: right;
    color: #999;
  }
  .project-title {
    font-weight: bold;
    color: #222;
  }
</style>
"""
TEMPLATE = """
# {name}

<div class="contact">
  <a href="{email}">{email}</a> &nbsp; | &nbsp;
  {phone_number} &nbsp; | &nbsp;
  <a href="{linkedin}">LinkedIn</a> &nbsp; | &nbsp;
  <a href="{github}">{github}</a> &nbsp; | &nbsp;
  <a href="{personal_website}">Personal Website</a>
</div>

---

## Profile

Results-driven software engineer with 7+ years of experience building scalable web platforms, leading cross-functional teams, and mentoring junior developers. Passionate about clean code, problem solving, and building impactful digital products.

---

## Experience
{experience}

---

## Education
{education}

---

## Skills
{skills}

---

## Projects
{projects}

---

## Certifications
{certificates}

---

## Languages
{languages}

"""
DRIVERNAME = "postgresql+psycopg"


def _get_info_for_cv(mode: str) -> dict[str, str]:
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
    engine = create_engine(url_oject)
    SQLModel.metadata.create_all(engine)
    model_classes = (
        ProgrammingLanguage,
        Language,
        Tool,
        Certificate,
        Charity,
        Education,
        Experience,
        Project,
    )
    with Session(engine) as session:
        profile_query = session.execute(
            select(Profile)
        ).first()  # TODO: Add checks for currently logged user
        links_query = session.execute(select(SocialPlatform))
        firstname = profile_query.firstname if profile_query else ""
        middlename = profile_query.middle_name if profile_query else ""
        surname = profile_query.surname if profile_query else ""
        output = {
            "name": f"{firstname} {middlename} {surname}",
        }
        if mode == "llm-selection":
            links_arr = (link.link for link in links_query)
            output["links"] = ",".join(links_arr)
            for c in model_classes:
                query = session.execute(select(c))
                arr = (row for row in query)
                output["skills"] += ",".join(arr)
        else:
            output["links"] = {}
            for link in links_query:
                output["links"][link.name] = link.link
            output["skills"] = ""
            for c in model_classes:
                query = session.execute(select(c))
                arr = (row for row in query)
                output[c.__name__] = ",".join(arr)
        return output


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
        info = _get_info_for_cv(mode)
        skills = info["skills"]
        profile = (
            info["profile"]["firstname"]
            + info["profile"]["secondname"]
            + info["profile"]["surname"]
        )
        links = info["links"]
        prompt = f"Select skills and other qualifications from information: {skills} that match those of job requirements: {requirements}"
        response = send_req_to_llm(prompt)
        prompt = f"Create a cv in markdown, based upon these qualifications: {response}. Candidate information: {profile}. Links: {links}"
        cv = send_req_to_llm(prompt)
        for k, v in info.items():
            print(k, v)
    else:
        info = _get_info_for_cv(mode)
        cv = TEMPLATE.format(
            name=info.get("name", "Jan Kolon Movano"),
            email=info.get("email", "jakkolon123@gmail.com"),
            phone_number=info.get("phone_number", "+4 320 932 913"),
            linkedin=info.get("links", {}).get("linkedin", "https://linkedin.com"),
            github=info.get("links", {}).get("github", "https://github.com"),
            personal_website=info.get("links", {}).get(
                "personal_website", "https://personal_website.com"
            ),
            experience=info.get("experience", "placeholder"),
            education=info.get("education", "placeholder"),
            skills=info.get("skills", "placeholder"),
            projects=info.get("projects", "placeholder"),
            certificates=info.get("certificates", "placeholder"),
            languages=info.get("languages", "placeholder"),
        )

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
            format="html",
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
