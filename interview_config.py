"""
Interview Configuration
Set the position and other interview details here
"""

# Position for the interview
INTERVIEW_POSITION = "UI/UX Designer"  # Change this for different positions

# Company details (optional)
COMPANY_NAME = "Tacktile System"
DEPARTMENT = "Engineering"

# Interview settings
INTERVIEW_DURATION_TARGET = 20  # Target duration in minutes
QUESTION_DIFFICULTY = "intermediate"  # easy, intermediate, advanced

# Skills to focus on (customize per position)
KEY_SKILLS = {
    "AI Developer": [
        "Python",
        "Generative AI",
        "LLMs",
        "Machine Learning",
        "API Development",
        "PyTorch/TensorFlow"
    ],
    "Software Engineer": [
        "JavaScript",
        "Django",
        "REST APIs",
        "PostgreSQL",
        "AWS/Cloud",
        "Git",
        "Systems Design"
    ],
    "Backend Engineer": [
        "Java",
        "Springboot",
        "REST APIs",
        "MySQL",
        "MongoDB",
        "Git",
        "Systems Design"
    ],
    "Frontend Developer": [
        "React",
        "TypeScript",
        "CSS/Tailwind",
        "State Management",
        "REST APIs"
    ],
    "Data Scientist": [
        "Python",
        "Statistics",
        "Machine Learning",
        "SQL",
        "Data Visualization"
    ],
    "UI/UX Designer": [
        "Figma",
        "User Research",
        "Wireframing",
        "Prototyping",
        "Design Systems",
        "Design Decisions"
    ],
}

def get_interview_config():
    """Get the current interview configuration"""
    return {
        "position": INTERVIEW_POSITION,
        "company": COMPANY_NAME,
        "department": DEPARTMENT,
        "key_skills": KEY_SKILLS.get(INTERVIEW_POSITION, []),
        "duration_target": INTERVIEW_DURATION_TARGET,
        "difficulty": QUESTION_DIFFICULTY
    }



# # For Sales Executive
# INTERVIEW_POSITION = "Sales Executive"
# KEY_SKILLS = ["CRM", "Lead Generation", "Negotiation", "Communication", "Target Achievement"]

# # For BPO Agent
# INTERVIEW_POSITION = "Customer Service Agent"
# KEY_SKILLS = ["Communication", "Problem Solving", "CRM Software", "Patience", "Multitasking"]

# # For Bank Teller
# INTERVIEW_POSITION = "Bank Teller"
# KEY_SKILLS = ["Cash Handling", "Customer Service", "Banking Software", "Accuracy", "Compliance"]
