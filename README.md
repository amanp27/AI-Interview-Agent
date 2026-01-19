# AI Interview System - Python Backend

Complete AI-powered interview system backend built with Python, LiveKit, and Claude AI.

## Architecture

```
┌─────────────────┐
│   Frontend      │
│ (React/TypeScript)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │  ← api_server.py
│  (Port 8000)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LiveKit Room   │
│  + Recording    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐  ┌──────────┐
│Candidate│  │AI Agent  │ ← agent.py
│         │  │(Claude)  │
└─────────┘  └──────────┘
```

## Files Overview

### Core Files

1. **agent.py** - Main AI interview agent
   - Connects to LiveKit rooms
   - Manages conversation flow
   - Captures full transcript
   - Handles interview lifecycle

2. **api_server.py** - FastAPI REST API
   - Creates interview sessions
   - Generates LiveKit tokens
   - Manages interview data
   - Triggers evaluations

3. **tools.py** - Utilities and managers
   - TranscriptManager: Captures and stores conversations
   - EvaluationEngine: AI-powered candidate evaluation
   - RecordingManager: Manages video/audio recordings
   - InterviewStateManager: Tracks interview state

4. **prompts.py** - AI prompts and instructions
   - Agent instructions
   - Position-specific questions
   - Evaluation criteria
   - Dynamic prompt generation

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required credentials:
- **LiveKit**: Get from https://cloud.livekit.io (or run locally)
- **Anthropic API**: Get from https://console.anthropic.com
- **OpenAI API**: Get from https://platform.openai.com

### 3. Run LiveKit Server (Local Development)

If using local LiveKit server:

```bash
# Using Docker
docker run -d \
  --name livekit \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 7882:7882/udp \
  -e LIVEKIT_KEYS="devkey: devsecret" \
  livekit/livekit-server:latest

# Or download binary from https://github.com/livekit/livekit/releases
```

Update .env:
```
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=devsecret
```

### 4. Start the Backend Services

**Terminal 1: Start API Server**
```bash
python api_server.py
# Runs on http://localhost:8000
```

**Terminal 2: Start AI Agent**
```bash
python agent.py start
# Waits for interview sessions
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/

# Start interview
curl -X POST http://localhost:8000/api/start-interview \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "position": "Software Engineer",
    "experience": "5 years"
  }'
```

## How It Works

### 1. Interview Start Flow

```
Frontend → POST /api/start-interview
   ↓
API creates LiveKit room
   ↓
Generate tokens (candidate + agent)
   ↓
Initialize transcript tracking
   ↓
Return token to frontend
   ↓
AI Agent joins room automatically
   ↓
Interview begins
```

### 2. Conversation Capture

The system captures conversations in real-time:

```python
# In agent.py
async def on_user_speech(self, text: str):
    # Captures candidate responses
    self.transcript_manager.add_entry(
        interview_id=self.interview_id,
        speaker=self.candidate_name,
        text=text
    )

async def on_agent_speech(self, text: str):
    # Captures AI interviewer questions
    self.transcript_manager.add_entry(
        interview_id=self.interview_id,
        speaker="AI Interviewer",
        text=text
    )
```

### 3. Recording Process

LiveKit automatically records:
- **Video**: Full interview with both participants
- **Audio**: High-quality audio tracks
- **Separate tracks**: Individual audio for analysis

Recordings are saved and can be accessed via API.

### 4. AI Evaluation

After interview ends:

```python
# Automatically triggered
transcript = get_full_transcript()
   ↓
Claude analyzes conversation
   ↓
Generates comprehensive evaluation:
   - Overall score (0-100)
   - Technical assessment
   - Communication score
   - Problem-solving ability
   - Strengths & weaknesses
   - Hiring recommendation
   ↓
Saved to evaluations/{interview_id}_evaluation.json
```

## API Endpoints

### Start Interview
```http
POST /api/start-interview
Content-Type: application/json

{
  "name": "John Doe",
  "position": "Senior Software Engineer",
  "experience": "5 years"
}

Response:
{
  "token": "eyJhbGc...",
  "room_name": "interview-uuid",
  "interview_id": "uuid",
  "ws_url": "wss://..."
}
```

### End Interview
```http
POST /api/end-interview
Content-Type: application/json

{
  "interview_id": "uuid"
}
```

### Get Interview Details
```http
GET /api/interview/{interview_id}

Response:
{
  "interview_id": "uuid",
  "candidate_name": "John Doe",
  "position": "Senior Software Engineer",
  "status": "completed",
  "transcript": [...],
  "evaluation": {...}
}
```

### List All Interviews
```http
GET /api/interviews?status=completed&page=1&page_size=10
```

### Get Transcript
```http
GET /api/transcript/{interview_id}
```

### Get Evaluation
```http
GET /api/evaluation/{interview_id}
```

## Customization

### Adding New Position Types

Edit `prompts.py`:

```python
POSITION_QUESTIONS = {
    "your_position": [
        "Question 1 for this role",
        "Question 2 for this role",
    ]
}
```

### Adjusting Interview Duration

Edit `agent.py`:

```python
# Change threshold for wrapping up
if state_manager.should_wrap_up(interview_id, threshold=15):
    # Now interviews will have ~15 exchanges before wrapping up
```

### Custom Evaluation Criteria

Edit `prompts.py` - `EVALUATION_PROMPT`:

```python
# Add custom scoring dimensions
"custom_score": <0-100>,
"custom_assessment": "Your custom criteria"
```

## Data Storage

The system stores data in local files (for testing):

```
project/
├── transcripts/
│   └── {interview_id}_transcript.json
├── evaluations/
│   └── {interview_id}_evaluation.json
├── recordings/
│   └── {interview_id}_recording.mp4
└── agent_tokens.json
```

For production, integrate with:
- **MongoDB**: For structured data
- **AWS S3**: For recordings
- **PostgreSQL**: For relational data

## Monitoring and Logs

View logs in real-time:

```bash
# API Server logs
tail -f logs/api.log

# Agent logs
tail -f logs/agent.log
```

## Troubleshooting

### LiveKit Connection Issues

```bash
# Check LiveKit is running
curl http://localhost:7880

# Verify credentials
echo $LIVEKIT_API_KEY
```

### Agent Not Joining Rooms

```bash
# Check agent is running
ps aux | grep agent.py

# Restart agent
python agent.py start
```

### Transcript Not Saving

```bash
# Check file permissions
ls -la transcripts/

# Verify directory exists
mkdir -p transcripts evaluations recordings
```

### Evaluation Not Generating

```bash
# Check Anthropic API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

## Production Deployment

### Using Render/Railway/Heroku

1. Add `Procfile`:
```
web: uvicorn api_server:app --host 0.0.0.0 --port $PORT
worker: python agent.py start
```

2. Set environment variables in platform
3. Deploy

### Using Docker

```dockerfile
# Dockerfile provided separately
docker build -t ai-interview .
docker run -p 8000:8000 ai-interview
```

### Using LiveKit Cloud

1. Sign up at https://cloud.livekit.io
2. Create project
3. Get API credentials
4. Update .env with cloud URL and keys

## Next Steps

1. ✅ Backend running locally
2. 🔄 Build React frontend
3. 🔄 Connect frontend to backend
4. 🔄 Test full interview flow
5. 🔄 Add recording playback
6. 🔄 Deploy to production

## Support

For issues:
1. Check logs
2. Verify environment variables
3. Ensure all services are running
4. Check API documentation

---

Built with ❤️ using Python, LiveKit, and Claude AI