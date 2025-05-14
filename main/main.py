# main.py
import asyncio
import logging
from livekit import agents
from livekit.agents import AgentSession, RoomInputOptions, AutoSubscribe
from livekit.plugins import groq, cartesia, deepgram, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from agent import GreetingAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("livekit-agent")

async def entrypoint(ctx: agents.JobContext):
    logger.info("Connecting to room and waiting for participants")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    await ctx.wait_for_participant()
    logger.info("Participant connected, initializing assistant")

    assistant = GreetingAgent()

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    logger.info("Starting agent session")
    await session.start(
        room=ctx.room,
        agent=assistant,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

if __name__ == "__main__":
    logger.info("Starting LiveKit agent application")
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
