from dotenv import load_dotenv
import os

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import (
    openai,
    noise_cancellation,
    bey
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
    
    # Initialize Beyond Presence avatar AFTER session starts (optional)
    try:
        avatar_id = os.getenv("BEY_AVATAR_ID")
        avatar_key = os.getenv("BEY_API_KEY")
        
        if avatar_id and avatar_key:
            # Create avatar session
            avatar = bey.AvatarSession(
                avatar_id=avatar_id,
                api_key=avatar_key,
            )
            # Start avatar with both agent_session and room
            await avatar.start(
                agent_session=session,
                room=ctx.room
            )
            print("✅ Beyond Presence avatar connected successfully")
        else:
            print("⚠️ Beyond Presence avatar not configured - running without avatar")
            print("   Add BEY_AVATAR_ID and BEY_API_KEY to .env file to enable avatar")
    except Exception as e:
        print(f"⚠️ Could not initialize avatar: {e}")
    
    # Generate initial greeting using SESSION_INSTRUCTION
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION
    )


if __name__ == "__main__":
    agents.cli.run_app(server)