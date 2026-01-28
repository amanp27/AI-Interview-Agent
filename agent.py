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
    
    # Create the interview assistant instance
    assistant = InterviewAssistant()
    
    # Don't set position from config - let it be detected from candidate
    # assistant.interview_tools.set_candidate_details(position=config["position"])
    
    print(f"📋 Interview Session Started")
    print(f"   Company: Tacktile System")
    print(f"   Mode: Adaptive (Position will be detected from candidate's introduction)")
    print(f"   Status: Ready to interview any role\n")
    
    # Initialize the session with OpenAI Realtime model
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="coral",
            temperature=0.8,  # Higher for more natural, human-like responses
        ),
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
                    print(f"📝 Captured: {speaker[:4]}... ({len(text)} chars)")
                    
        except Exception as e:
            print(f"⚠️ Error capturing conversation: {e}")
            import traceback
            traceback.print_exc()
    
    # Add error handler for session
    @session.on("error")
    def on_session_error(error):
        """Handle session errors"""
        print(f"❌ Session error occurred: {error}")
    
    # Add handler for when agent starts speaking
    @session.on("agent_started_speaking")
    def on_agent_speaking():
        """Track when agent speaks"""
        print("🗣️ Agent started speaking...")
    
    # Add handler for when agent stops speaking
    @session.on("agent_stopped_speaking") 
    def on_agent_stopped():
        """Track when agent stops"""
        print("🤐 Agent stopped speaking")
    
    # Track if evaluation has been generated
    evaluation_generated = False
    
    # Room disconnect handler - fires when user leaves
    @ctx.room.on("participant_disconnected")
    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        """Handle participant disconnect"""
        nonlocal evaluation_generated
        if not evaluation_generated and participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_STANDARD:
            print(f"\n👋 Participant {participant.identity} disconnected")
            print(f"💬 Total conversation turns: {len(assistant.interview_tools.transcript)}")
            evaluation_generated = True
            # Schedule evaluation
            import asyncio
            asyncio.create_task(generate_post_interview_evaluation(assistant.interview_tools))
    
    # Also handle room disconnection (backup)
    @ctx.room.on("disconnected")
    def on_room_disconnected():
        """Handle room disconnect (backup trigger)"""
        nonlocal evaluation_generated
        if not evaluation_generated and len(assistant.interview_tools.transcript) > 0:
            print(f"\n🔌 Room disconnected")
            print(f"💬 Total conversation turns: {len(assistant.interview_tools.transcript)}")
            evaluation_generated = True
            import asyncio
            asyncio.create_task(generate_post_interview_evaluation(assistant.interview_tools))
    
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


async def generate_post_interview_evaluation(interview_tools: InterviewTools):
    """
    Generate comprehensive evaluation after interview concludes
    
    Args:
        interview_tools: The InterviewTools instance with all interview data
    """
    try:
        print("\n" + "="*70)
        print("🔍 Generating Interview Evaluation...")
        print("="*70 + "\n")
        
        # Get all interview data
        interview_data = interview_tools.get_interview_data_for_evaluation()
        
        # Check if we have enough data
        transcript_length = len(interview_tools.transcript)
        if transcript_length == 0:
            print("⚠️  No conversation captured - Session ended too early")
            print("    Skipping evaluation generation.")
            return
        
        print(f"✅ Captured {transcript_length} conversation turns")
        
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