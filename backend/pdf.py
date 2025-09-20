from sqlalchemy import URL
from sqlmodel import SQLModel, create_engine, Session, select
from dotenv import load_dotenv
from weasyprint import HTML, CSS

# from app_setup import engine
from backend.llm import send_req_to_llm
from backend.models import (
    ProfileModel,
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
import datetime
import logging


logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
PDF_ENGINE = "weasyprint"
CV_DIR_NAME = "cv"

# TODO: Use HTML and CSS instead of markdown. Maybe try latex in the future
STYLING = """
body {
font-family: Arial, sans-serif;
max-width: 900px;
margin: auto;
padding: 2rem;
line-height: 1.6;
color: #333;
}
h1 {
text-align: center;
font-size: 2em;
margin-bottom: 0.5em;
}
.contact {
display: flex;
justify-content: space-between;
flex-wrap: wrap;
font-size: 0.95em;
margin-bottom: 2rem;
}
section {
margin-bottom: 2rem;
}
h2 {
border-bottom: 1px solid #aaa;
font-size: 1.3em;
margin-bottom: 0.5em;
}
h3 {
margin: 0.5em 0 0.2em;
font-weight: bold;
}
.meta {
font-size: 0.9em;
color: #666;
display: flex;
justify-content: space-between;
flex-wrap: wrap;
}
ul {
margin-top: 0.3em;
padding-left: 1.2em;
}
li {
margin-bottom: 0.4em;
}
"""
TEMPLATE = """
<h1>{name}</h1>
<div class="contact">
<div>
<strong>Email:</strong>{email}
</div>
<div>
<strong>Phone:</strong>{phone_number}
</div>
<div>
<strong><a href="{github}">GitHub</a></strong>
</div>
<div>
<strong><a href="{linkedin}">LinkedIn</a></strong>
</div>
<div>
<strong><a href="{personal_website}">Personal Website</a></strong>
</div>
</div>
<section>
<h2>Education</h2>
{education}
</section>
<section>
<h2>Experience</h2>
{experience}
</section>
<section>
<h2>Skills</h2>
{skills}
{languages}
</section>
<section>
<h2>Projects</h2>
{projects}
</section>
"""
DRIVERNAME = "postgresql+psycopg"


def _get_info_for_cv(profile: ProfileModel, mode: str) -> dict[str, str]:
    load_dotenv()
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
        links_query = session.execute(
            select(SocialPlatform).where(SocialPlatform.profile_id == profile.id)
        )
        output = {
            "name": f"{profile.firstname} {profile.middlename} {profile.surname}",
            "email": profile.email,
            # "phone_number": profile.phone_number,
        }
        if mode == "llm-selection" or mode == "llm-generation":
            links_arr = (link.link for link in links_query)
            output["links"] = ",".join(links_arr)
            output["skills"] = ""
            for c in model_classes:
                query = session.execute(select(c).where(c.profile_id == profile.id))
                arr = (row for row in query)
                output["skills"] += ",".join(arr)
        elif mode == "user-cv":
            output["links"] = {}
            for link in links_query:
                output["links"][link.name] = link.link
            output["skills"] = ""
            for c in model_classes:
                query = session.execute(select(c).where(c.profile_id == profile.id))
                arr = (row for row in query)
                output[c.__name__] = ",".join(arr)
        return output


def create_cv(
    profile: ProfileModel,
    posting_id: str,
    requirements: str,
    location: str,
    company_url: str,
    mode: str = "llm-selection",
) -> Path:
    # TODO: Here we will get data from the database
    # TODO: Make LLM compare and choose skills etc. that fit the description and then add them to the template:
    # 1) Get and process LLM output to put it into the template
    # 2) Make LLM put adequate skills etc. into the template string
    # 3) Make LLM write the CV from the ground up
    # 4) Make algorithm for putting relevant skills into CV without use of LLM
    info = _get_info_for_cv(profile, mode)
    if mode == "llm-selection":
        skills = info.get("skills", "")
        name = info.get("name", "Jan Kolon Movano")
        links = info.get("links", "")
        prompt = f"Select skills and other qualifications from information: {skills} that match those of job requirements: {requirements}"
        response = send_req_to_llm(prompt)
        prompt = f"Put all the relevant information: {skills}, {name}, {links}. Into this template: {TEMPLATE}\nWhere each {{}} tells you where to put which category of information"
        cv = send_req_to_llm(prompt)
    elif mode == "llm-generation":
        skills = info.get("skills", "")
        name = info.get("name", "Jan Kolon Movano")
        links = info.get("links", "")
        logging.info(f"name: {name}\nskills: {skills}\nlinks: {links}")
        prompt = f"Select skills and other qualifications from information: {skills} that match those of job requirements: {requirements}"
        response = send_req_to_llm(prompt)
        prompt = f"Generate a complete personal CV page using only HTML and CSS with no additional comments or explanations, based upon these qualifications: {response}. Name: {name}. Social media links: {links}"
        cv = send_req_to_llm(prompt).lstrip("```html").rstrip("```")
    elif mode == "user-cv":
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

    logging.info(f"CV:\n{cv}")

    current_time = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S")
    cv_path = Path().joinpath(CV_DIR_NAME).joinpath(f"{current_time}_{posting_id}.pdf")

    if not os.path.isdir(CV_DIR_NAME):
        os.mkdir(CV_DIR_NAME)

    HTML(string=cv).write_pdf(cv_path, stylesheets=[CSS(string=STYLING)])

    return cv_path
