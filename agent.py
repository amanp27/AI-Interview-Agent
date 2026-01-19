from dotenv import load_dotenv

import os

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import (
    openai,
    noise_cancellation,
    bey
)

from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import InterviewTools

load_dotenv(".env")


class InterviewAssistant(Agent):
    """AI Interview Assistant Agent"""
    
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_INSTRUCTION)
        # Store tools separately, not as self.tools
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
            voice="coral",  # You can change to: alloy, echo, fable, onyx, nova, shimmer
            temperature=0.8
        )
    )

    avatar = bey.AvatarSession(
        avatar_id = os.getenv("BEY_AVATAR_ID"),
        api_key = os.getenv("BEY_API_KEY")
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
    
    # Generate initial greeting
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION
    )


if __name__ == "__main__":
    agents.cli.run_app(server)