import datetime
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from sqlmodel import Session, select
from weasyprint import CSS, HTML

from backend.config import settings
from backend.database.crud import get_model, get_skills, get_user_preferences
from backend.database.models import (
    CertificateModel,
    CharityModel,
    EducationModel,
    ExperienceModel,
    LanguageModel,
    LocationModel,
    ProgrammingLanguageModel,
    ProjectModel,
    SocialPlatformModel,
    ToolModel,
    UserModel,
    WebsiteModel,
)
from backend.llm import send_req_to_llm
from backend.logging import get_logger
from backend.prompts import load_prompt
from backend.scrapers.base_scraper import JobEntry

logger = get_logger()
PDF_ENGINE = "weasyprint"
CV_DIR_NAME = settings.ROOT_DIR / "cv"

DEFAULT_STYLING = """
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


class Skills(BaseModel):
    programming_languages: list[ProgrammingLanguageModel]
    languages: list[LanguageModel]
    tools: list[ToolModel]
    certificates: list[CertificateModel]


class CVOutput(BaseModel):
    html: str
    css: str


def get_data(user: UserModel, session: Session) -> dict:
    model_classes = [
        LocationModel,
        ProgrammingLanguageModel,
        LanguageModel,
        ToolModel,
        CertificateModel,
        CharityModel,
        EducationModel,
        ExperienceModel,
        ProjectModel,
        SocialPlatformModel,
        WebsiteModel,
    ]
    d = {
        f"{model_class.__class__.__name__.replace('Model', '').lower()}"
        + "s": session.exec(
            select(model_class).where(model_class.user_id == user.id)
        ).all()
        for model_class in model_classes
    }
    for key, val in d.items():
        new_values = []
        for model in val:
            tmp = model.dump_model()
            tmp.pop("id")
            tmp.pop("user_id")
            new_values.append(tmp)
        d[key] = new_values

    return d


async def create_cv(
    user: UserModel,
    session: Session,
    job_entry: JobEntry,
    mode: Literal[
        "llm-generation", "llm-selection", "no-llm-generation", "user-specified"
    ] = "llm-selection",
) -> Path:
    # TODO: Make LLM compare and choose skills etc. that fit the description and then add them to the template:
    # 1) Get and process LLM output to put it into the template
    # 2) Make LLM put adequate skills etc. into the template string
    # 3) Make LLM write the CV from the ground up
    # 4) Make algorithm for putting relevant skills into CV without use of LLM
    data = get_data(user=user, session=session)
    skills = Skills.model_validate(get_skills(session=session, user=user))
    requirements = {
        "requirements": job_entry.requirements,
        "duties": job_entry.duties,
    }
    social_platforms = get_model(
        session=session, user=user, model=SocialPlatformModel
    )
    experience = get_model(session=session, user=user, model=ExperienceModel)
    charity = get_model(session=session, user=user, model=CharityModel)
    education = get_model(session=session, user=user, model=EducationModel)
    candidate_data = {
        "name": f"{user.first_name} {user.middle_name} {user.surname}",
        "email": user.email,
        "phone_number": user.phone_number,
    }

    if mode == "llm-generation":
        skills_chosen_by_llm = await send_req_to_llm(
            system_prompt=await load_prompt(
                prompt_path="cv:system:skill_selection"
            ),
            prompt=await load_prompt(
                prompt_path="cv:user:skill_selection",
                skills=skills,
                requirements=requirements,
            ),
        )
        cv = await send_req_to_llm(
            system_prompt=await load_prompt(
                prompt_path="cv:system:cv_generation"
            ),
            prompt=await load_prompt(
                prompt_path="cv:user:cv_generation",
                skills_chosen_by_llm=skills_chosen_by_llm,
                candidate_data=candidate_data,
                social_platforms=social_platforms,
                experience=experience,
                charity=charity,
                education=education,
            ),
            use_json_schema=True,
            model=CVOutput,
        )
    elif mode == "llm-selection":
        skills_chosen_by_llm = await send_req_to_llm(
            system_prompt=await load_prompt(
                prompt_path="cv:system:skill_selection"
            ),
            prompt=await load_prompt(
                prompt_path="cv:user:skill_selection",
                skills=skills,
                requirements=requirements,
            ),
        )
        cv = send_req_to_llm(
            prompt=await load_prompt(
                "cv:user:cv_insert_skills",
                skills=skills_chosen_by_llm,
                name=candidate_data.get("name", ""),
                social_platforms=social_platforms,
                template=TEMPLATE,
            )
        )
    elif mode == "no-llm-generation":
        html = TEMPLATE.format(
            name=candidate_data.get("name", ""),
            email=candidate_data.get("email", ""),
            phone_number=candidate_data.get("phone_number", ""),
            linkedin=data.get("links", {}).get(
                "linkedin", "https://linkedin.com"
            ),
            github=data.get("links", {}).get("github", "https://github.com"),
            personal_website=data.get("links", {}).get(
                "personal_website", "https://personal_website.com"
            ),
            # experience=.get("experiences", ""),
            # education=.get("education", ""),
            skills=data.get("skills", ""),
            # projects=.get("projects", ""),
            certificates=skills.get("certificates", ""),
            languages=skills.get("languages", ""),
        )
        cv = CVOutput(html=html, css=DEFAULT_STYLING)
    elif mode == "user-specified":
        if user_preferences := get_user_preferences(session, user):
            return Path(user_preferences.cv_path)
        else:
            # TODO: Fallback to other methods of cv creation
            cv = ""
    else:
        cv = ""

    logger.info(f"CV:\n{cv}")

    current_time = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S")
    cv_path = (
        CV_DIR_NAME
        / f"{job_entry.title}_{current_time}.pdf"  # TODO: change job_entry.title
    )

    if not os.path.isdir(CV_DIR_NAME):
        os.mkdir(CV_DIR_NAME)

    if cv:
        HTML(string=cv.html).write_pdf(
            cv_path, stylesheets=[CSS(string=cv.css)]
        )
    else:
        HTML(string=cv).write_pdf(
            cv_path, stylesheets=[CSS(string=DEFAULT_STYLING)]
        )

    return cv_path
