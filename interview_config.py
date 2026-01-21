"""
Interview Configuration
Set the position and other interview details here
"""

# Position for the interview
INTERVIEW_POSITION = "AI Developer"  # Change this for different positions

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
        "Machine Learning",
        "LLMs",
        "API Development",
        "PyTorch/TensorFlow"
    ],
    "Software Engineer": [
        "Python",
        "Django/FastAPI",
        "REST APIs",
        "PostgreSQL",
        "AWS/Cloud"
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
    ]
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