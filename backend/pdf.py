import markdown
import pdfkit



def _create_cv(description: str, location: str, company_url: str) -> str:
    css = """
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
    template = """
      # {name}

      <div class="contact">
        📧 <a href="mailto:{email}">{email}</a> &nbsp; | &nbsp;
        📞 {phone_number} &nbsp; | &nbsp;
        <a href="{linkedin}">LinkedIn</a> &nbsp; | &nbsp;
        <a href="{github}">GitHub</a> &nbsp; | &nbsp;
        <a href="{personal_website}">Website</a>
      </div>

      ---

      ## 🧑‍💼 Profile
      {profile}

      ---

      ## 💼 Experience
      {experience}

      ---

      ## 🎓 Education
      {education}

      ---

      ## 🛠️ Skills
      {skills}

      ---

      ## 📂 Projects
      {projects}

      ---

      ## 📜 Certifications
      {certificates}

      ---

      ## 💬 Languages
      {languages}
    """

    # TODO: Here we will get data from the database
    name = ""
    email = ""
    phone_number = ""
    linkedin = ""
    github = ""
    personal_website = ""
    profile = ""
    experience = ""
    education = ""
    skills = ""
    projects = ""
    certificates = ""
    languages = ""

    # TODO: Make LLM compare and choose skills etc. that fit the description and then add them to the template:
    # 1) Simply get and process LLM output to put it into the template
    # 2) Make LLM put adequate skills etc. into the template string

    html = markdown.markdown(template)
    pdfkit.from_string(css + html, "cv.pdf")

    # return template.format(
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


if __name__ == "__main__":
    _create_cv("fas", "", "")
