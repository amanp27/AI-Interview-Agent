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
    
    # Initialize the session with OpenAI Realtime model
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="coral",  # Professional voice
            temperature=0.6,  # Lower for more consistent, concise responses
        )
    )
    
    # Setup event handlers for transcript capture
    @session.on("agent_speech")
    def on_agent_speech(text: str):
        """Capture agent's speech to transcript"""
        assistant.interview_tools.add_to_transcript("interviewer", text)
    
    @session.on("user_speech") 
    def on_user_speech(text: str):
        """Capture candidate's speech to transcript"""
        assistant.interview_tools.add_to_transcript("candidate", text)
    
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
    
    print("✅ Interview session started - transcript capture enabled")
    
    # Generate initial greeting using SESSION_INSTRUCTION
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION
    )
    
    # Monitor for interview completion
    try:
        # Wait for session to complete
        await session.wait_for_completion()
    except Exception as e:
        print(f"Session ended: {e}")
    finally:
        # Generate evaluation after interview concludes
        await generate_post_interview_evaluation(assistant.interview_tools)


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
        if not interview_data["transcript"] or interview_data["transcript"] == "No transcript available.":
            print("⚠️  Warning: No transcript captured. Evaluation will be based on notes only.")
        
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