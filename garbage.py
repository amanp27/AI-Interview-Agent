from dotenv import load_dotenv
import os

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import (
    openai,
    noise_cancellation,
)

from prompts import (
    SYSTEM_INSTRUCTION, 
    AGENT_INSTRUCTION, 
    SESSION_INSTRUCTION,
    INTERVIEW_OBJECTIVE,
    QUESTION_POLICY,
    EVALUATION_GUIDELINES,
    CLOSING_INSTRUCTION
)
from tools import InterviewTools
from evaluation import InterviewEvaluator
from interview_config import get_interview_config

load_dotenv(".env")


class InterviewAssistant(Agent):
    """AI Interview Assistant Agent - SIMA from Tacktile System"""
    
    def __init__(self) -> None:
        # Combine all relevant instructions for the agent's persistent behavior
        full_instructions = f"""{SYSTEM_INSTRUCTION}

{AGENT_INSTRUCTION}

{INTERVIEW_OBJECTIVE}

{QUESTION_POLICY}

{EVALUATION_GUIDELINES}

{CLOSING_INSTRUCTION}"""
        
        super().__init__(instructions=full_instructions)
        # Store tools separately
        self.interview_tools = InterviewTools()


server = AgentServer()


@server.rtc_session()
async def interview_agent(ctx: agents.JobContext):
    """Main interview agent session handler"""
    
    # Get interview configuration
    config = get_interview_config()
    
    # Create the interview assistant instance
    assistant = InterviewAssistant()
    
    # Set the position from config
    assistant.interview_tools.set_candidate_details(position=config["position"])
    
    print(f"📋 Interview Configuration:")
    print(f"   Position: {config['position']}")
    print(f"   Company: {config['company']}")
    print(f"   Key Skills: {', '.join(config['key_skills'])}\n")
    
    # STT with transcription enabled (for observability)
    stt = openai.STT(
        model="gpt-4o-transcribe",
        language="en"
    )
    
    # Initialize the session with OpenAI Realtime model
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="coral",
            temperature=0.6,
        ),
        stt=stt,  # Add STT for transcript capture
    )
    
    # Event handler to capture conversation items
    @session.on("conversation_item_added")
    def on_conversation_item_added(item):
        """Capture conversation to transcript"""
        try:
            if hasattr(item, 'role') and hasattr(item, 'content'):
                role = item.role  # 'user' or 'assistant'
                
                # Extract text from content
                text = ""
                if isinstance(item.content, str):
                    text = item.content
                elif isinstance(item.content, list):
                    # Handle list of content items
                    for content_item in item.content:
                        if hasattr(content_item, 'text'):
                            text += content_item.text
                        elif isinstance(content_item, dict) and 'text' in content_item:
                            text += content_item['text']
                
                if text:
                    # Map role to speaker
                    speaker = "candidate" if role == "user" else "interviewer"
                    assistant.interview_tools.add_to_transcript(speaker, text)
                    
        except Exception as e:
            print(f"Error capturing conversation item: {e}")
    
    try:
        # Start the session with room configuration
        await session.start(
            room=ctx.room,
            agent=assistant,
            room_options=room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(
                    noise_cancellation=lambda params: noise_cancellation.BVCTelephony() 
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP 
                    else noise_cancellation.BVC(),
                ),
            ),
        )
        
        print("✅ Interview session started (Observability + Transcription enabled)")
        
        # Generate initial greeting using SESSION_INSTRUCTION
        await session.generate_reply(
            instructions=SESSION_INSTRUCTION
        )
        
        # Wait for session to complete
        await session.wait_for_completion()
        
    except Exception as e:
        print(f"❌ Session error: {e}")
        
    finally:
        # Generate evaluation after interview concludes
        await generate_post_interview_evaluation(assistant.interview_tools, session)
        
        # Close session so Insights upload
        await session.close()
        print("🛑 Session closed cleanly (Insights uploaded)")


async def generate_post_interview_evaluation(interview_tools: InterviewTools, session: AgentSession):
    """
    Generate comprehensive evaluation after interview concludes
    
    Args:
        interview_tools: The InterviewTools instance with all interview data
        session: The AgentSession to extract additional data from
    """
    try:
        print("\n" + "="*70)
        print("🔍 Generating Interview Evaluation...")
        print("="*70 + "\n")
        
        # Extract candidate name from conversation if available
        if session.history and len(session.history) > 1:
            # Try to extract name from first user response
            for item in session.history:
                if hasattr(item, 'role') and item.role == 'user':
                    # Extract text from first user message
                    if hasattr(item, 'content'):
                        content = item.content
                        if isinstance(content, str) and "my name is" in content.lower():
                            # Simple name extraction
                            parts = content.lower().split("my name is")
                            if len(parts) > 1:
                                name = parts[1].strip().split()[0].capitalize()
                                interview_tools.set_candidate_details(name=name)
                                break
        
        # Get all interview data
        interview_data = interview_tools.get_interview_data_for_evaluation()
        
        # Check if we have enough data
        if not interview_data["transcript"] or interview_data["transcript"] == "No transcript available.":
            print("⚠️  Warning: Limited transcript data. Evaluation will be based on available notes.")
        
        # Create evaluator and run assessment
        evaluator = InterviewEvaluator()
        evaluation = await evaluator.evaluate_interview(
            candidate_name=interview_data["candidate_name"],
            position=interview_data["position"],
            transcript=interview_data["transcript"],
            interview_notes=interview_data["interview_notes"],
            duration_minutes=interview_data["duration_minutes"],
            candidate_info=interview_data["candidate_info"]
        )
        
        # Print summary report
        summary_report = evaluator.generate_summary_report(evaluation)
        print(summary_report)
        
        # Print file location
        print(f"\n✅ Full evaluation saved to: {evaluation['metadata']['saved_to']}")
        print(f"📊 Overall Recommendation: {evaluation['recommendation']['decision']}")
        print(f"📈 Role Fit: {evaluation['recommendation']['role_fit_percentage']}%")
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error generating evaluation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    agents.cli.run_app(server)