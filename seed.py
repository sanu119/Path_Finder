from app import create_app, db
from app.models import User, Profile, Career, Skill, CareerSkill, Resource

app = create_app()

SKILLS = [
("Python", "Programming"), ("Java", "Programming"), ("JavaScript", "Web"), ("TypeScript", "Web"), ("C++", "Programming"),
("SQL", "Data"), ("HTML", "Web"), ("CSS", "Web"), ("React", "Web"), ("Node.js", "Web"), ("Flask", "Backend"),
("Django", "Backend"), ("Git", "Tools"), ("GitHub", "Tools"), ("REST APIs", "Backend"), ("Data Structures", "CS Fundamentals"),
("Algorithms", "CS Fundamentals"), ("OOP", "CS Fundamentals"), ("DBMS", "Data"), ("Statistics", "Data"), ("Pandas", "Data"),
("NumPy", "Data"), ("Matplotlib", "Data"), ("Power BI", "Analytics"), ("Excel", "Analytics"), ("Machine Learning", "AI/ML"),
("Scikit-learn", "AI/ML"), ("Deep Learning", "AI/ML"), ("TensorFlow", "AI/ML"), ("PyTorch", "AI/ML"), ("NLP", "AI/ML"),
("Cybersecurity Fundamentals", "Security"), ("Networking", "Security"), ("Linux", "Systems"), ("OWASP", "Security"), ("SIEM", "Security"),
("Figma", "Design"), ("UX Research", "Design"), ("Wireframing", "Design"), ("Prototyping", "Design"), ("Design Systems", "Design"),
("Cloud Fundamentals", "Cloud"), ("AWS", "Cloud"), ("Azure", "Cloud"), ("Docker", "Cloud"), ("Kubernetes", "Cloud"), ("CI/CD", "DevOps"),
("Communication", "Professional"), ("Problem Solving", "Professional"), ("System Design", "Architecture"),
]

CAREERS = {
"Software Developer": ["Programming", ["Python","Java","Data Structures","Algorithms","OOP","DBMS","SQL","Git","GitHub","REST APIs","Problem Solving","Communication"]],
"Web Developer": ["Development", ["HTML","CSS","JavaScript","TypeScript","React","Node.js","REST APIs","SQL","Git","GitHub","Problem Solving","Communication"]],
"Data Analyst": ["Data & Analytics", ["Excel","SQL","Statistics","Python","Pandas","NumPy","Matplotlib","Power BI","DBMS","Git","Problem Solving","Communication"]],
"Data Scientist": ["Data & AI", ["Python","SQL","Statistics","Pandas","NumPy","Matplotlib","Machine Learning","Scikit-learn","Deep Learning","DBMS","Git","Communication"]],
"AI/ML Engineer": ["Artificial Intelligence", ["Python","Data Structures","Algorithms","Statistics","NumPy","Pandas","Machine Learning","Scikit-learn","Deep Learning","TensorFlow","PyTorch","Git","Problem Solving"]],
"Cybersecurity Analyst": ["Cybersecurity", ["Cybersecurity Fundamentals","Networking","Linux","OWASP","SIEM","Python","SQL","Git","Problem Solving","Communication","Cloud Fundamentals"]],
"UI/UX Designer": ["Design", ["Figma","UX Research","Wireframing","Prototyping","Design Systems","HTML","CSS","Communication","Problem Solving","GitHub"]],
"Cloud Engineer": ["Cloud & DevOps", ["Cloud Fundamentals","AWS","Azure","Linux","Docker","Kubernetes","CI/CD","Networking","Python","Git","GitHub","System Design","Problem Solving"]],
}

RESOURCE_MAP = {
"Python": ("Python Official Tutorial", "https://docs.python.org/3/tutorial/", "Docs"),
"JavaScript": ("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "Docs"),
"HTML": ("MDN HTML", "https://developer.mozilla.org/en-US/docs/Web/HTML", "Docs"),
"CSS": ("MDN CSS", "https://developer.mozilla.org/en-US/docs/Web/CSS", "Docs"),
"SQL": ("SQLBolt", "https://sqlbolt.com/", "Practice"),
"Git": ("Git Documentation", "https://git-scm.com/doc", "Docs"),
"React": ("React Learn", "https://react.dev/learn", "Course"),
"Flask": ("Flask Documentation", "https://flask.palletsprojects.com/", "Docs"),
"Pandas": ("Pandas Getting Started", "https://pandas.pydata.org/docs/getting_started/", "Docs"),
"Statistics": ("Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability", "Course"),
"Machine Learning": ("Google Machine Learning Crash Course", "https://developers.google.com/machine-learning/crash-course", "Course"),
"Figma": ("Figma Learn", "https://help.figma.com/hc/en-us/categories/360002051613", "Docs"),
"AWS": ("AWS Skill Builder", "https://skillbuilder.aws/", "Course"),
"Docker": ("Docker Get Started", "https://docs.docker.com/get-started/", "Docs"),
"Cybersecurity Fundamentals": ("CISA Cybersecurity Resources", "https://www.cisa.gov/topics/cyber-threats-and-advisories", "Reference"),
}

with app.app_context():
    # Seed is intentionally idempotent: it creates missing records without duplicating existing data.
    admin = User.query.filter_by(email="admin@pathfinder.local").first()
    if not admin:
        admin = User(email="admin@pathfinder.local", role="admin")
        admin.set_password("Admin@123")
        admin.profile = Profile(name="Pathfinder Admin")
        db.session.add(admin)

    skills = {}
    for name, category in SKILLS:
        skill = Skill.query.filter_by(name=name).first()
        if not skill:
            skill = Skill(name=name, category=category, description=f"Build practical ability in {name}.")
            db.session.add(skill)
            db.session.flush()
        skills[name] = skill

    for career_name, (category, names) in CAREERS.items():
        career = Career.query.filter_by(name=career_name).first()
        if not career:
            career = Career(name=career_name, category=category, description=f"A structured Pathfinder route for becoming a {career_name}.")
            db.session.add(career)
            db.session.flush()
        existing = {x.skill_id for x in career.career_skills}
        for idx, name in enumerate(names):
            if skills[name].id not in existing:
                level = 3 if idx < 2 else 2
                priority = "High" if idx < 4 else ("Medium" if idx < 9 else "Low")
                db.session.add(CareerSkill(career_id=career.id, skill_id=skills[name].id, required_level=level, priority=priority, order_index=idx))

    db.session.flush()
    for skill_name, (title, url, rtype) in RESOURCE_MAP.items():
        skill = skills[skill_name]
        if not Resource.query.filter_by(title=title, skill_id=skill.id).first():
            db.session.add(Resource(title=title, url=url, resource_type=rtype, skill_id=skill.id))

    db.session.commit()
    print("Seed complete.")
    print("Demo admin: admin@pathfinder.local / Admin@123")
    print(f"Careers: {Career.query.count()} | Skills: {Skill.query.count()} | Resources: {Resource.query.count()}")
