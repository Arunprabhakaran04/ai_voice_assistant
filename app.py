from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    groq,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from prompts import WELCOME_MESSAGE, INSTRUCTIONS, LOOKUP_VIN_MESSAGE
from api import AssistantFnc


load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        # Initialize the agent with just the instructions parameter
        # Since chat_ctx doesn't accept 'instructions', we'll pass our instructions directly to Agent
        super().__init__(instructions=INSTRUCTIONS)

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    # Use generate_reply to send the welcome message
    await session.generate_reply(
        instructions=WELCOME_MESSAGE.strip()
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))