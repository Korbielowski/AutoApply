import datetime
import os
from pathlib import Path
from typing import Literal

from sqlmodel import Session, select
from weasyprint import CSS, HTML

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
from backend.scrapers.base_scraper import JobEntry

logger = get_logger()
PDF_ENGINE = "weasyprint"
CV_DIR_NAME = "cv"

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
    skills = get_skills(session=session, user=user)
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
    html, css = "", ""

    if mode == "llm-generation":
        select_skills_system_prompt = """
        You are an evaluation assistant whose exclusive role is to compare a candidate’s skills, experience, and qualifications with a specified job description.
        Your responsibilities are strictly limited to:
            1. Extracting job requirements from the provided job description.
            2. Extracting the candidate’s skills and qualifications from user-provided information.
            3. Identifying which of the candidate’s skills and qualifications directly match the job requirements.
            4. Returning only the matching skills and qualifications.
            5. If no matches exist, return 'False'.
        Rules and constraints:
            - Do not list missing skills, partial matches, extra skills, summaries, or recommendations.
            - Do not generate resumes, rewrite content, or provide career advice.
            - Do not infer qualifications that were not explicitly provided by the user.
            - Output must be factual, concise, and limited strictly to the overlapping skills/qualifications.
        """
        prompt = f"Select candidates skills and qualifications: {skills} that match those of job requirements: {requirements}"
        skills_chosen_by_llm = send_req_to_llm(
            system_prompt=select_skills_system_prompt, prompt=prompt
        )
        create_cv_system_prompt = """
        You are an assistant that outputs only two files in plain text:
            1. A complete HTML document containing the CV structure.
            2. A complete CSS stylesheet containing all styling.
        No other text, explanations, comments, or metadata may be included.
        Requirements:
            - No external imports, libraries, fonts, scripts, CDNs, or frameworks are allowed in either HTML or CSS.
            - No <style> blocks, no <script> tags, and no inline CSS attributes in the HTML. All styling must reside in the <style> tag.
            - The resulting rendered page must fit onto exactly one PDF page when printed on A4 (210mm × 297mm). Ensure content, spacing, and typography guarantee that no content flows to a second printed page.
            - Use semantic HTML5 elements (header, main, section, article, footer, nav as appropriate).
            - The layout must be clean, professional, responsive, and print-friendly.
            - Use only system fonts (e.g., a sensible system font stack) and basic CSS features. Do not reference or load web fonts.
            - Provide sections only for the data explicitly provided by the user. Include, when present in the supplied data:
            - Name & contact (email, phone, location, optionally LinkedIn/website)
            - Professional summary
            - Work experience (company, role, location, start/end dates, 3–6 bullet responsibilities/achievements per job)
            - Education
            - Skills (grouped where appropriate)
            - Projects (title + 1–2-line description)
            - Certifications / Awards
            - Languages
            - Omit any section for which no data is provided.
            - Do not invent or infer any qualifications, dates, or content not explicitly provided in the candidate data.
            - Do not output comments in either the HTML or CSS files.
            - Do not include analytics, tracking, or any non-declarative content.
            - Ensure the visual hierarchy is clear: distinct headings, readable body text, aligned dates/roles, and printer-visible links.
            - Ensure printable page margins and that links are visible in print.
        If the provided candidate data lacks optional fields, simply omit those items from the output file.
        """
        prompt = f"Generate a complete personal CV page using only HTML and CSS with no additional comments or explanations, based upon these qualifications and skills: {skills_chosen_by_llm}. candidate data: {candidate_data}. Social media accounts: {social_platforms}. Experience: {experience}. Charity involvement: {charity}. Education: {education}"
        response = await send_req_to_llm(
            system_prompt=create_cv_system_prompt, prompt=prompt
        )  # .lstrip("```html").rstrip("```")
        html, css = response.replace(
            "", ""
        )  # TODO: Split response into html and css properly
    elif mode == "llm-selection":
        prompt = f"Select candidates skills and qualifications: {data.get('tool')} that match those of job requirements: {requirements}"
        response = send_req_to_llm(prompt)
        prompt = f"Put all the relevant information: {skills}, {candidate_data.get('name', '')}, {social_platforms}. Into this template: {TEMPLATE}\nWhere each {{}} tells you where to put which category of information"
        cv = send_req_to_llm(prompt)
    elif mode == "no-llm-generation":
        cv = ""
        # cv = TEMPLATE.format(
        #     name=candidate_data.get("name", ""),
        #     email=candidate_data.get("email", ""),
        #     phone_number=candidate_data.get("phone_number", ""),
        #     linkedin=info.get("links", {}).get(
        #         "linkedin", "https://linkedin.com"
        #     ),
        #     github=info.get("links", {}).get("github", "https://github.com"),
        #     personal_website=info.get("links", {}).get(
        #         "personal_website", "https://personal_website.com"
        #     ),
        #     # experience=.get("experiences", ""),
        #     # education=.get("education", ""),
        #     skills=info.get("skills", ""),
        #     # projects=.get("projects", ""),
        #     certificates=skills.get("certificates", ""),
        #     languages=skills.get("languages", ""),
        # )
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
        Path()
        .joinpath(CV_DIR_NAME)
        .joinpath(f"{job_entry.title}_{current_time}.pdf")
    )  # TODO: change job_entry.title

    if not os.path.isdir(CV_DIR_NAME):
        os.mkdir(CV_DIR_NAME)

    if html and css:
        HTML(string=html).write_pdf(cv_path, stylesheets=[CSS(string=css)])
    else:
        HTML(string=cv).write_pdf(
            cv_path, stylesheets=[CSS(string=DEFAULT_STYLING)]
        )

    return cv_path
