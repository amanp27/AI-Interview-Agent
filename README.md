# 🎙️ AI Interview Assistant - SIMA

> **Intelligent, Adaptive Interview System powered by AI**  
> Conduct professional, real-time voice interviews across any role - from Software Engineers to Sales Executives.

[![LiveKit](https://img.shields.io/badge/LiveKit-Powered-blue)](https://livekit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green)](https://openai.com)
[![Python](https://img.shields.io/badge/Python-3.13-yellow)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-red)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Demo](#demo)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Evaluation System](#evaluation-system)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🌟 Overview

**SIMA (Smart Interview Management Assistant)** is an AI-powered voice interview system developed by **Tacktile System**. It conducts professional, real-time interviews with candidates, adapts to any job role, and provides comprehensive AI-driven evaluations to help make hiring decisions.

### What Makes SIMA Special?

- ✅ **100% Voice-Based** - Natural conversation, no typing required
- ✅ **Role-Adaptive** - Automatically detects candidate's role and asks relevant questions
- ✅ **Experience-Aware** - Adjusts difficulty for freshers vs experienced professionals
- ✅ **Real-Time Transcription** - Full conversation captured and analyzed
- ✅ **AI Evaluation** - Comprehensive scoring and hiring recommendations

---

## 🚀 Key Features

### 🎯 Intelligent Interview Conduct

| Feature | Description |
|---------|-------------|
| **Adaptive Questioning** | Detects role (UI/UX, Backend, Frontend, AI/ML, etc.) and asks relevant questions |
| **Experience Detection** | Automatically adjusts for freshers vs experienced candidates |
| **Conversational AI** | Natural, human-like dialogue - not robotic |
| **English Enforcement** | Strictly enforces English-only interviews |
| **Time Management** | Completes interviews in 20-25 minutes efficiently |
| **Bluff Detection** | Challenges vague answers and detects memorized responses |

### 📊 Comprehensive Evaluation

- **AI-Powered Analysis** using GPT-4
- **Multi-Dimensional Scoring** (Technical, Problem-Solving, Communication, Experience, Culture Fit)
- **Detailed Reports** in JSON format
- **Hiring Recommendations** (Strong Hire / Hire / Maybe / No Hire)
- **Role Fit Percentage** (0-100%)
- **Actionable Feedback** for candidates and hiring teams

### 🔧 Technical Capabilities

- **Real-Time Voice** via LiveKit & OpenAI Realtime API
- **Session Recording** - Audio, video, and transcripts automatically saved
- **Observability Dashboard** - Track interviews in LiveKit Cloud
- **Noise Cancellation** - Clear audio even in noisy environments
- **Multi-Role Support** - Tech, Design, Sales, HR, BPO, Banking, and more

---

## 🎬 Demo

### Interview Flow

```
1. Candidate joins → SIMA greets warmly
2. Candidate introduces → SIMA detects role (e.g., "Backend Developer")
3. Comfort phase → "What interests you about backend development?"
4. Technical questions → Role-specific (APIs, databases, etc.)
5. Project discussion → "Tell me about a recent project"
6. Behavioral questions → Teamwork, problem-solving
7. Wrap-up → "Any questions for me?"
8. Auto-evaluation → Comprehensive report generated
```

### Sample Evaluation Output

```
╔══════════════════════════════════════════════════════════════════╗
║                 INTERVIEW EVALUATION REPORT                      ║
╚══════════════════════════════════════════════════════════════════╝

CANDIDATE INFORMATION:
  Name:          Aman
  Position:      AI Developer
  Duration:      15 minutes

OVERALL ASSESSMENT:
  Recommendation: No Hire
  Overall Score:  3/10
  Role Fit:       30%

STRENGTHS:
  1. Experience building AI interview bot
  2. Familiar with Docker and AWS

WEAKNESSES:
  1. Limited technical depth in AI/ML concepts
  2. Unable to answer fundamental questions
  
✅ Saved to: evaluations/Aman_AI_Developer_20260123.json
```

---

## 🏗️ Architecture

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for detailed system design.

**High-Level Overview:**

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Candidate  │◄────►│  LiveKit     │◄────►│   SIMA      │
│  (Browser)  │WebRTC│  Server      │      │  AI Agent   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │ Observability│      │  OpenAI     │
                     │  Dashboard   │      │  GPT-4      │
                     └──────────────┘      └─────────────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │ Evaluation  │
                                           │   (JSON)    │
                                           └─────────────┘
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.13+
- OpenAI API Key
- LiveKit Cloud Account (free tier available)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/amanp27/AI-Interview-Agent.git
cd AI-Interview-Agent

# 2. Create virtual environment
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` file:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
```

### Run Interview Assistant

```bash
# Start in development mode
python agent.py dev

# You'll see:
# ✅ Interview session started
# 📋 Mode: Adaptive (Position detected from candidate)
# 🎯 Ready to interview any role
```

### Access Interview

1. Open LiveKit Playground: `https://your-livekit-url.livekit.cloud`
2. Join the room
3. Start speaking - SIMA will greet you!

---

## ⚙️ Configuration

### Customize Interview Settings

Edit `interview_config.py`:

```python
# Company details
DEPARTMENT = "Engineering"

# Interview settings
INTERVIEW_DURATION_TARGET = 20  # minutes
QUESTION_DIFFICULTY = "intermediate"  # easy, intermediate, advanced

# Supported roles (auto-detected)
KEY_SKILLS = {
    "AI Developer": ["Python", "ML", "LLMs", "PyTorch"],
    "Backend Developer": ["Java", "Spring", "REST APIs", "MySQL"],
    "UI/UX Designer": ["Figma", "User Research", "Prototyping"],
    # Add more roles as needed
}
```

### Customize Prompts

Edit `prompts.py` to customize:
- `SYSTEM_INSTRUCTION` - Core behavior and boundaries
- `AGENT_INSTRUCTION` - Interview flow and structure  
- `QUESTION_POLICY` - Question types and rules
- `EVALUATION_GUIDELINES` - Scoring criteria

---

## 📖 Usage

### 1. Conducting Interviews

```bash
# Start the agent
python agent.py dev

# Candidate joins via LiveKit
# SIMA automatically:
# ✅ Detects their role
# ✅ Adapts questions
# ✅ Manages time
# ✅ Generates evaluation
```

### 2. Generating Evaluations Manually

If auto-evaluation didn't trigger, use the manual script:

```bash
# Generate evaluation from chat history JSON
python generate_evaluation_from_json.py candidate_chat_history.json

# Output:
# ✅ Extracted 58 conversation turns
# 👤 Candidate: Aman
# 💼 Detected Position: AI Developer
# 📊 Overall Recommendation: No Hire
# ✅ Saved to: evaluations/Aman_AI_Developer_20260123.json
```

### 3. Accessing Saved Evaluations

```python
from evaluation import InterviewEvaluator

evaluator = InterviewEvaluator()

# List all evaluations
evaluations = evaluator.list_evaluations()
print(evaluations)

# Load specific evaluation
eval_data = evaluator.load_evaluation("Aman_AI_Developer_20260123.json")

# Generate report
report = evaluator.generate_summary_report(eval_data)
print(report)
```

---

## 📊 Evaluation System

### Scoring Dimensions (Out of 10)

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Technical Skills | 35% | Role-specific knowledge and expertise |
| Problem-Solving | 25% | Analytical thinking and approach |
| Communication | 15% | Clarity and articulation |
| Practical Experience | 20% | Real-world application |
| Cultural Fit | 5% | Teamwork and collaboration |

### Evaluation Output

```json
{
  "metadata": {
    "candidate_name": "John Doe",
    "position": "Backend Developer",
    "duration_minutes": 18
  },
  "ratings": {
    "overall_score": 7,
    "technical_competency": 8,
    "soft_skills": 6,
    "experience_match": 7,
    "growth_potential": 7
  },
  "recommendation": {
    "decision": "Hire",
    "role_fit_percentage": 75,
    "next_steps": "Proceed to technical round"
  }
}
```

### Recommendation Levels

- **Strong Hire** (9-10/10) - Exceeds requirements
- **Hire** (7-8/10) - Meets requirements well
- **Maybe** (5-6/10) - Borderline candidate
- **No Hire** (1-4/10) - Significant gaps

---

## 📁 Project Structure

```
AI-Interview-Agent/
├── agent.py                 # Main agent server
├── prompts.py              # Interview prompts and instructions
├── tools.py                # Interview tools and utilities
├── evaluation.py           # AI evaluation engine
├── interview_config.py     # Configuration settings
├── generate_evaluation_from_json.py  # Manual evaluation script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── evaluations/            # Saved evaluation reports (JSON)
├── Json_conversation/      # Chat history files
└── README.md              # This file
```

---

## 🔧 Troubleshooting

### Agent Not Responding

**Issue:** Agent starts but doesn't speak

**Solution:**
```bash
# Stop with Ctrl+C
# Restart
python agent.py dev
```

**Check:**
- OpenAI API key is valid and has credits
- LiveKit connection is stable
- Microphone permissions are granted

### Evaluation Not Generating

**Issue:** Interview completes but no evaluation file

**Solution:**
```bash
# Generate manually from chat history
python generate_evaluation_from_json.py your_chat_history.json
```

**Note:** Chat history JSONs are automatically downloaded from LiveKit Observability dashboard.

### Position Not Detected

**Issue:** Shows "Unknown Position" in evaluation

**Solution:**
- Candidate must clearly state their role in introduction
- Use keywords: "I'm a Backend Developer", "UI/UX Designer", etc.
- If still not detected, position will be inferred from conversation content

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `OpenAI API key not found` | Missing .env file | Copy .env.example to .env and add key |
| `FileNotFoundError: evaluations/` | Folder doesn't exist | Folder created automatically on first run |
| `Connection refused` | LiveKit server down | Check LIVEKIT_URL in .env |

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Test thoroughly before submitting
- Update documentation as needed

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Developed by Tacktile System**

- **AI/ML Engineer:** Aman Prajapati

---

## 🙏 Acknowledgments

- [LiveKit](https://livekit.io) - Real-time communication infrastructure
- [OpenAI](https://openai.com) - GPT-4 and Realtime API
- [Anthropic](https://anthropic.com) - Claude assistance in development

---

## 📈 Roadmap

- [ ] Multi-language support (Spanish, French, Hindi)
- [ ] Video recording and analysis
- [ ] Integration with ATS systems
- [ ] Batch interview processing
- [ ] Custom evaluation criteria per company
- [ ] Interview analytics dashboard
- [ ] MongoDB integration for data persistence

---

<div align="center">

</div>