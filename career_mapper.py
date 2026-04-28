"""
Career Guidance - Skills to Job Roles Mapping
"""

CAREER_MAP = {
    "Data Science": {
        "roles": [
            {"title": "Data Analyst", "salary": "$65,000 - $95,000", "growth": "25%"},
            {"title": "Data Scientist", "salary": "$95,000 - $140,000", "growth": "35%"},
            {"title": "Machine Learning Engineer", "salary": "$110,000 - $160,000", "growth": "40%"},
            {"title": "Business Intelligence Analyst", "salary": "$70,000 - $110,000", "growth": "20%"}
        ],
        "top_skills": ["Python", "SQL", "Statistics", "Machine Learning", "Data Visualization"]
    },
    "Artificial Intelligence": {
        "roles": [
            {"title": "AI Engineer", "salary": "$120,000 - $180,000", "growth": "45%"},
            {"title": "Research Scientist", "salary": "$130,000 - $200,000", "growth": "30%"},
            {"title": "NLP Engineer", "salary": "$115,000 - $165,000", "growth": "42%"},
            {"title": "Computer Vision Engineer", "salary": "$110,000 - $160,000", "growth": "38%"}
        ],
        "top_skills": ["Python", "TensorFlow", "PyTorch", "Deep Learning", "NLP", "Computer Vision"]
    },
    "Web Development": {
        "roles": [
            {"title": "Frontend Developer", "salary": "$70,000 - $120,000", "growth": "23%"},
            {"title": "Full Stack Developer", "salary": "$85,000 - $140,000", "growth": "28%"},
            {"title": "Backend Developer", "salary": "$80,000 - $130,000", "growth": "25%"},
            {"title": "Web Architect", "salary": "$120,000 - $180,000", "growth": "18%"}
        ],
        "top_skills": ["JavaScript", "React", "Node.js", "TypeScript", "HTML/CSS", "REST APIs"]
    },
    "Mobile Development": {
        "roles": [
            {"title": "Mobile App Developer", "salary": "$75,000 - $125,000", "growth": "22%"},
            {"title": "iOS Developer", "salary": "$90,000 - $140,000", "growth": "20%"},
            {"title": "Android Developer", "salary": "$85,000 - $135,000", "growth": "21%"},
            {"title": "Cross-Platform Developer", "salary": "$80,000 - $130,000", "growth": "26%"}
        ],
        "top_skills": ["Swift", "Kotlin", "Flutter", "React Native", "Mobile UI Design", "Firebase"]
    },
    "Cloud Computing": {
        "roles": [
            {"title": "Cloud Architect", "salary": "$130,000 - $190,000", "growth": "35%"},
            {"title": "DevOps Engineer", "salary": "$100,000 - $150,000", "growth": "30%"},
            {"title": "Site Reliability Engineer", "salary": "$120,000 - $170,000", "growth": "32%"},
            {"title": "Cloud Security Engineer", "salary": "$115,000 - $165,000", "growth": "38%"}
        ],
        "top_skills": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Linux"]
    },
    "Cybersecurity": {
        "roles": [
            {"title": "Security Analyst", "salary": "$75,000 - $115,000", "growth": "35%"},
            {"title": "Penetration Tester", "salary": "$85,000 - $130,000", "growth": "30%"},
            {"title": "SOC Analyst", "salary": "$70,000 - $110,000", "growth": "32%"},
            {"title": "Security Architect", "salary": "$130,000 - $190,000", "growth": "28%"}
        ],
        "top_skills": ["Network Security", "Ethical Hacking", "SIEM", "Risk Assessment", "Cryptography"]
    },
    "Business & Management": {
        "roles": [
            {"title": "Product Manager", "salary": "$95,000 - $150,000", "growth": "25%"},
            {"title": "Project Manager", "salary": "$80,000 - $130,000", "growth": "20%"},
            {"title": "Business Analyst", "salary": "$70,000 - $110,000", "growth": "22%"},
            {"title": "Strategy Consultant", "salary": "$100,000 - $160,000", "growth": "18%"}
        ],
        "top_skills": ["Project Management", "Agile", "Data Analysis", "Leadership", "Communication"]
    },
    "Design": {
        "roles": [
            {"title": "UI/UX Designer", "salary": "$75,000 - $125,000", "growth": "24%"},
            {"title": "Product Designer", "salary": "$85,000 - $140,000", "growth": "26%"},
            {"title": "Visual Designer", "salary": "$65,000 - $105,000", "growth": "18%"},
            {"title": "Design Lead", "salary": "$110,000 - $160,000", "growth": "20%"}
        ],
        "top_skills": ["Figma", "Adobe XD", "Prototyping", "User Research", "Visual Design"]
    }
}

def get_career_guidance(category):
    """Get career guidance for a course category"""
    return CAREER_MAP.get(category, {
        "roles": [
            {"title": "Specialist", "salary": "$60,000 - $100,000", "growth": "15%"}
        ],
        "top_skills": ["Technical Skills", "Problem Solving", "Communication"]
    })

def get_job_roles_for_skills(skills_list):
    """Get job roles based on skills"""
    roles = []
    for category, data in CAREER_MAP.items():
        category_skills = [s.lower() for s in data["top_skills"]]
        matching_skills = [s for s in skills_list if s.lower() in category_skills]
        if matching_skills:
            roles.extend(data["roles"])
    
    # Remove duplicates
    seen = set()
    unique_roles = []
    for role in roles:
        if role["title"] not in seen:
            seen.add(role["title"])
            unique_roles.append(role)
    
    return unique_roles[:4] if unique_roles else []

def format_salary(salary_str):
    """Format salary string"""
    return salary_str

def get_growth_emoji(growth_str):
    """Get emoji based on growth percentage"""
    growth_num = int(growth_str.replace("%", ""))
    if growth_num >= 35:
        return "🚀"
    elif growth_num >= 25:
        return "📈"
    else:
        return "✅"

