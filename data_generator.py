"""
Course Dataset Generator
Generates 1200+ realistic courses across 8+ categories
"""
import pandas as pd
import numpy as np
import random
import os
from faker import Faker

fake = Faker()

# Define course categories and their sub-topics
CATEGORIES = {
    "Data Science": [
        "Python for Data Science", "Machine Learning", "Deep Learning", "Statistics",
        "Data Visualization", "Pandas & NumPy", "SQL for Data Science", "Big Data Analytics",
        "Time Series Analysis", "Natural Language Processing", "Computer Vision",
        "Reinforcement Learning", "MLOps", "Feature Engineering", "Data Mining"
    ],
    "Artificial Intelligence": [
        "AI Fundamentals", "Neural Networks", "Generative AI", "LLMs & Transformers",
        "AI Ethics", "Robotics", "Autonomous Systems", "AI for Healthcare",
        "Prompt Engineering", "AI Agent Development", "Multi-modal AI", "Edge AI"
    ],
    "Web Development": [
        "HTML & CSS", "JavaScript", "React.js", "Node.js", "Full Stack Development",
        "Django", "Flask", "Next.js", "TypeScript", "Web Security", "REST APIs",
        "GraphQL", "Microservices", "Web Performance", "Progressive Web Apps"
    ],
    "Mobile Development": [
        "Android Development", "iOS Development", "Flutter", "React Native",
        "Swift", "Kotlin", "Mobile UI/UX", "App Store Optimization",
        "Cross-platform Development", "Mobile Security"
    ],
    "Cloud Computing": [
        "AWS Fundamentals", "Azure", "Google Cloud", "DevOps", "Kubernetes",
        "Docker", "Terraform", "CI/CD Pipelines", "Serverless Architecture",
        "Cloud Security", "Site Reliability Engineering", "Infrastructure as Code"
    ],
    "Cybersecurity": [
        "Ethical Hacking", "Network Security", "Penetration Testing", "Cryptography",
        "Security Operations", "Threat Intelligence", "Digital Forensics",
        "Cloud Security", "Application Security", "SOC Analyst"
    ],
    "Business & Management": [
        "Project Management", "Agile & Scrum", "Product Management", "Digital Marketing",
        "Business Analytics", "Leadership", "Communication Skills", "Financial Analysis",
        "Entrepreneurship", "Supply Chain Management", "HR Management"
    ],
    "Design": [
        "UI/UX Design", "Graphic Design", "Adobe Photoshop", "Figma",
        "Motion Graphics", "3D Modeling", "Blender", "Design Systems",
        "User Research", "Prototyping", "Visual Design"
    ]
}

PLATFORMS = ["Udemy", "Coursera", "edX", "LinkedIn Learning", "Pluralsight", "Skillshare", "DataCamp", "freeCodeCamp"]
LEVELS = ["Beginner", "Intermediate", "Advanced"]
DURATIONS = ["2-5 hours", "5-10 hours", "10-20 hours", "20-40 hours", "40+ hours"]

# Skills mapping for each category
SKILLS_MAP = {
    "Data Science": ["Python", "R", "SQL", "Machine Learning", "Statistics", "Pandas", "NumPy", "Matplotlib", "Seaborn", "Scikit-learn", "TensorFlow", "PyTorch", "Data Cleaning", "EDA", "Predictive Modeling"],
    "Artificial Intelligence": ["Python", "TensorFlow", "PyTorch", "Neural Networks", "Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning", "LLMs", "Transformers", "OpenAI API", "Hugging Face"],
    "Web Development": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Express", "MongoDB", "SQL", "TypeScript", "Next.js", "REST API", "Git", "Docker"],
    "Mobile Development": ["Java", "Kotlin", "Swift", "Dart", "Flutter", "React Native", "Firebase", "Mobile UI Design", "App Testing", "iOS SDK", "Android SDK"],
    "Cloud Computing": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD", "Jenkins", "Linux", "Python", "Bash", "Monitoring"],
    "Cybersecurity": ["Network Security", "Linux", "Python", "Wireshark", "Metasploit", "Kali Linux", "SIEM", "Incident Response", "Risk Assessment", "Compliance"],
    "Business & Management": ["Project Management", "Agile", "Scrum", "Data Analysis", "Excel", "PowerPoint", "Communication", "Leadership", "Strategic Planning", "Marketing"],
    "Design": ["Figma", "Adobe XD", "Photoshop", "Illustrator", "Sketch", "Prototyping", "Wireframing", "User Research", "Color Theory", "Typography"]
}

# Instructor names pool
INSTRUCTORS = [
    "Dr. Andrew Ng", "Angela Yu", "Jose Portilla", "Maximilian Schwarzmüller",
    "Jonas Schmedtmann", "Dr. Angela Yu", "Colt Steele", "Stephen Grider",
    "Andrei Neagoie", "Brad Traversy", "Dr. Yuval Noah Harari", "Dr. Fei-Fei Li",
    "Dr. Sebastian Thrun", "Dr. Yann LeCun", "Tim Buchalka", "Rob Percival",
    "Academind", "Zero to Mastery", "DataCamp Instructors", "Google Cloud Training",
    "Microsoft Learn", "AWS Training", "Meta Blueprint", "IBM Skills Network",
    "Stanford Online", "MIT Open Learning", "Harvard Online", "UC Berkeley Extension"
]

def generate_course_description(title, category, skills):
    """Generate realistic course descriptions"""
    templates = [
        f"Master {title} with this comprehensive course. Learn {', '.join(skills[:3])} through hands-on projects and real-world applications. Perfect for professionals looking to advance their career in {category}.",
        f"This {title} course covers everything from fundamentals to advanced concepts. You'll gain practical skills in {', '.join(skills[:4])} and build a portfolio of projects.",
        f"Learn {title} from industry experts. This course provides in-depth training on {', '.join(skills[:3])} with practical exercises and certification preparation.",
        f"Become proficient in {title}. This comprehensive program teaches {', '.join(skills[:4])} through interactive lessons, quizzes, and capstone projects.",
        f"Start your journey in {title} today. Master {', '.join(skills[:3])} with step-by-step guidance from experienced instructors in the {category} field."
    ]
    return random.choice(templates)

def generate_courses(num_courses=1200):
    """Generate synthetic course dataset"""
    courses = []
    
    for i in range(num_courses):
        category = random.choice(list(CATEGORIES.keys()))
        topic = random.choice(CATEGORIES[category])
        
        # Generate title variations
        title_variants = [
            f"{topic}: Complete Guide",
            f"{topic} Masterclass",
            f"Learn {topic} from Scratch",
            f"Advanced {topic}",
            f"{topic} Bootcamp",
            f"{topic} Certification",
            f"Practical {topic}",
            f"{topic} for Professionals",
            f"The Complete {topic} Course",
            f"{topic} Fundamentals"
        ]
        title = random.choice(title_variants)
        
        # Select skills
        available_skills = SKILLS_MAP[category]
        num_skills = random.randint(4, 8)
        skills = random.sample(available_skills, min(num_skills, len(available_skills)))
        
        # Generate description
        description = generate_course_description(topic, category, skills)
        
        # Other attributes
        instructor = random.choice(INSTRUCTORS)
        platform = random.choice(PLATFORMS)
        level = random.choice(LEVELS)
        duration = random.choice(DURATIONS)
        
        # Price based on level and platform
        base_price = random.randint(20, 200)
        if level == "Advanced":
            base_price += 30
        if platform in ["Coursera", "edX"]:
            base_price = min(base_price, 100)
        price = round(base_price, 2)
        
        # Rating
        rating = round(random.uniform(3.5, 4.9), 1)
        
        # Course link
        slug = title.lower().replace(" ", "-").replace(":", "").replace("&", "and")[:50]
        link = f"https://{platform.lower().replace(' ', '')}.com/course/{slug}-{random.randint(1000, 9999)}"
        
        course = {
            "course_id": f"COURSE_{i+1:05d}",
            "title": title,
            "category": category,
            "description": description,
            "instructor": instructor,
            "platform": platform,
            "course_link": link,
            "price": price,
            "rating": rating,
            "duration": duration,
            "level": level,
            "skills": ", ".join(skills),
            "num_reviews": random.randint(50, 5000)
        }
        courses.append(course)
    
    return pd.DataFrame(courses)

def main():
    print("Generating 1200+ courses dataset...")
    df = generate_courses(1200)
    
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    # Save to CSV
    output_path = "models/course_dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Dataset saved to {output_path}")
    print(f"📊 Total courses: {len(df)}")
    print(f"📚 Categories: {df['category'].nunique()}")
    print("\nCategory distribution:")
    print(df['category'].value_counts())
    
    return df

if __name__ == "__main__":
    main()

