"""
Generate evaluation from saved chat history JSON
Run this if evaluation didn't auto-generate after interview
"""

import asyncio
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# CRITICAL: Load environment variables FIRST
load_dotenv(".env")

from evaluation import InterviewEvaluator
from interview_config import get_interview_config

async def generate_evaluation_from_json(json_file_path: str):
    """
    Generate evaluation report from LiveKit chat history JSON
    
    Args:
        json_file_path: Path to the chat history JSON file
    """
    
    print(f"\n{'='*70}")
    print(f"📄 Loading chat history from: {json_file_path}")
    print(f"{'='*70}\n")
    
    # Load JSON file
    with open(json_file_path, 'r') as f:
        chat_data = json.load(f)
    
    # Extract conversation items
    items = chat_data.get('items', [])
    
    # Build transcript and detect role
    transcript_parts = []
    candidate_name = "Unknown Candidate"
    candidate_position = "Unknown Position"
    
    for item in items:
        if item.get('type') == 'message':
            role = item.get('role')
            content = item.get('content', [])
            
            # Extract text from content
            if isinstance(content, list) and len(content) > 0:
                text = content[0] if isinstance(content[0], str) else ""
            else:
                text = str(content)
            
            if text:
                # Map role to speaker
                speaker = "Candidate" if role == "user" else "Interviewer"
                transcript_parts.append(f"{speaker}: {text}")
                
                # Try to extract candidate name and position from first user message
                if role == "user" and candidate_name == "Unknown Candidate":
                    text_lower = text.lower()
                    
                    # Extract name
                    if "my name is" in text_lower or "i'm" in text_lower or "i am" in text_lower:
                        for pattern in ["my name is ", "i'm ", "i am "]:
                            if pattern in text_lower:
                                parts = text_lower.split(pattern)
                                if len(parts) > 1:
                                    name_part = parts[1].strip().split()[0]
                                    candidate_name = name_part.capitalize()
                                    break
                    
                    # Extract position/role - Look for common keywords
                    role_keywords = {
                        "ui/ux designer": "UI/UX Designer",
                        "ui ux designer": "UI/UX Designer",
                        "designer": "Designer",
                        "frontend developer": "Frontend Developer",
                        "front end developer": "Frontend Developer",
                        "backend developer": "Backend Developer",
                        "back end developer": "Backend Developer",
                        "full stack developer": "Full Stack Developer",
                        "fullstack developer": "Full Stack Developer",
                        "software developer": "Software Developer",
                        "software engineer": "Software Engineer",
                        "ai developer": "AI Developer",
                        "ml engineer": "ML Engineer",
                        "machine learning": "ML Engineer",
                        "data scientist": "Data Scientist",
                        "devops engineer": "DevOps Engineer",
                        "qa engineer": "QA Engineer",
                        "tester": "QA Tester",
                        "product manager": "Product Manager",
                        "project manager": "Project Manager",
                        "sales": "Sales Executive",
                        "marketing": "Marketing Specialist",
                        "hr": "HR Professional",
                    }
                    
                    for keyword, position in role_keywords.items():
                        if keyword in text_lower:
                            candidate_position = position
                            break
    
    # If still unknown, try to infer from conversation content
    if candidate_position == "Unknown Position":
        full_text = " ".join(transcript_parts).lower()
        if "angular" in full_text or "react" in full_text or "frontend" in full_text:
            candidate_position = "Frontend Developer"
        elif "backend" in full_text or "api" in full_text or "database" in full_text:
            candidate_position = "Backend Developer"
        elif "figma" in full_text or "design" in full_text or "wireframe" in full_text:
            candidate_position = "UI/UX Designer"
        elif "machine learning" in full_text or "model" in full_text or "ai" in full_text:
            candidate_position = "AI/ML Developer"
    
    # Build full transcript
    full_transcript = "\n\n".join(transcript_parts)
    
    print(f"✅ Extracted {len(transcript_parts)} conversation turns")
    print(f"👤 Candidate: {candidate_name}")
    print(f"💼 Detected Position: {candidate_position}\n")
    
    # Get interview config - but we'll use detected position instead
    config = get_interview_config()
    
    # Create mock interview notes
    interview_notes = [
        {
            "category": "general",
            "note": f"Interview conducted via LiveKit - {len(transcript_parts)} conversation turns",
            "stage": "summary"
        },
        {
            "category": "role_detection",
            "note": f"Candidate role detected as: {candidate_position}",
            "stage": "analysis"
        }
    ]
    
    # Calculate duration
    duration_minutes = 15  # Default
    if len(items) > 1:
        first_item = next((i for i in items if i.get('type') == 'message'), None)
        last_item = next((i for i in reversed(items) if i.get('type') == 'message'), None)
        
        if first_item and last_item:
            start_time = first_item.get('created_at', 0)
            end_time = last_item.get('created_at', 0)
            duration_minutes = int((end_time - start_time) / 60)
    
    print(f"⏱️  Interview duration: {duration_minutes} minutes\n")
    
    # Generate evaluation
    print(f"{'='*70}")
    print(f"🔍 Generating AI Evaluation...")
    print(f"{'='*70}\n")
    
    evaluator = InterviewEvaluator()
    evaluation = await evaluator.evaluate_interview(
        candidate_name=candidate_name,
        position=candidate_position,  # Use detected position
        transcript=full_transcript,
        interview_notes=interview_notes,
        duration_minutes=duration_minutes,
        candidate_info={
            "name": candidate_name,
            "position": candidate_position,  # Use detected position
            "source": "LiveKit Chat History JSON"
        }
    )
    
    # Print summary report
    summary_report = evaluator.generate_summary_report(evaluation)
    print(summary_report)
    
    # Print file location
    print(f"\n✅ Full evaluation saved to: {evaluation['metadata']['saved_to']}")
    print(f"📊 Overall Recommendation: {evaluation['recommendation']['decision']}")
    print(f"📈 Role Fit: {evaluation['recommendation']['role_fit_percentage']}%\n")
    print(f"{'='*70}\n")
    
    return evaluation


if __name__ == "__main__":
    # Check if JSON file provided
    if len(sys.argv) < 2:
        print("\n❌ No JSON file provided!")
        print("\n📖 Usage: python generate_evaluation_from_json.py <json_filename>")
        print("\n💡 Examples:")
        print("   python generate_evaluation_from_json.py p_64yg1tqalc3_RM_DNxSHzpBpqtT_chat_history.json")
        print("   python generate_evaluation_from_json.py aman_chat_history.json")
        print("\n📁 Note: Script will look for the file in 'Json_conversation/' folder\n")
        sys.exit(1)
    
    json_filename = sys.argv[1]
    
    # Check if it's just a filename or a full path
    if '/' in json_filename:
        # Full path provided
        json_file = Path(json_filename)
    else:
        # Just filename provided - look in Json_conversation folder
        json_file = Path("Json_conversation") / json_filename
    
    # Check if file exists
    if not json_file.exists():
        print(f"\n❌ Error: File not found: {json_file}")
        print(f"📁 Current directory: {Path.cwd()}")
        print(f"📄 Looking for: {json_file.absolute()}")
        
        # Try to list files in Json_conversation folder
        json_folder = Path("Json_conversation")
        if json_folder.exists():
            json_files = list(json_folder.glob("*.json"))
            if json_files:
                print(f"\n📂 Available JSON files in Json_conversation/:")
                for f in json_files:
                    print(f"   - {f.name}")
            else:
                print(f"\n⚠️ No JSON files found in Json_conversation/ folder")
        else:
            print(f"\n⚠️ Json_conversation/ folder does not exist")
        
        print()
        sys.exit(1)
    
    # Run evaluation
    asyncio.run(generate_evaluation_from_json(str(json_file)))