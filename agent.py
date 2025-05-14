from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, JobContext, AutoSubscribe
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
import logging
import re
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("livekit-agent")

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=INSTRUCTIONS)
        self.assistant_fnc = AssistantFnc()
        self._session = None  # Use internal variable for session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    async def on_message(self, message_text):
        """Handle incoming messages from users"""
        logger.info(f"Received message: {message_text[:50]}...")

        vin_pattern = r'\b[A-HJ-NPR-Z0-9]{17}\b'
        potential_vin = re.search(vin_pattern, message_text)

        if not self.assistant_fnc.has_car() and potential_vin:
            vin = potential_vin.group(0)
            logger.info(f"Detected potential VIN: {vin}")

            response = self.assistant_fnc.lookup_car(vin)

            if "not found" not in response:
                await self.session.generate_reply(
                    user_message=f"I found your car information. {response} How can I help you with your car today?"
                )
            else:
                await self.find_profile(message_text, failed_lookup=True)
        elif self.assistant_fnc.has_car():
            logger.info("Car profile exists, handling regular query")
            await self.handle_query(message_text)
        else:
            logger.info("No car profile, looking up car")
            await self.find_profile(message_text)

    async def find_profile(self, message_text, failed_lookup=False):
        system_message = LOOKUP_VIN_MESSAGE(message_text)
        if failed_lookup:
            system_message += "\n\nNote: A VIN was detected but no matching car was found. Please explain that the VIN wasn't found and ask for correct information."

        logger.info("Using lookup VIN message template")

        await self.session.generate_reply(
            instructions=system_message
        )

    async def handle_query(self, message_text):
        if "car details" in message_text.lower() or "show car" in message_text.lower():
            car_details = self.assistant_fnc.get_car_details()
            await self.session.generate_reply(
                user_message=f"Here are your current car details: {car_details}"
            )
        else:
            logger.info("Handling regular query with existing car profile")
            await self.session.generate_reply(
                user_message=message_text
            )

    async def process_function_call(self, function_name, **kwargs):
        logger.info(f"Processing function call: {function_name} with args: {kwargs}")

        if function_name == "lookup_car" and "vin" in kwargs:
            return self.assistant_fnc.lookup_car(kwargs["vin"])
        elif function_name == "get_car_details":
            return self.assistant_fnc.get_car_details()
        elif function_name == "create_car" and all(k in kwargs for k in ["vin", "make", "model", "year"]):
            return self.assistant_fnc.create_car(
                kwargs["vin"],
                kwargs["make"],
                kwargs["model"],
                int(kwargs["year"])
            )
        else:
            return "Function not found or missing required parameters"


def _format_message(message):
    if isinstance(message, list):
        return "\n".join("[image]" if hasattr(item, "image_url") else str(item) for item in message)
    return str(message)


async def entrypoint(ctx: JobContext):
    logger.info("Connecting to room and waiting for participants")
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()
    logger.info("Participant connected, initializing assistant")

    assistant = Assistant()

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

    assistant.session = session

    logger.info("Sending welcome message")
    await session.generate_reply(
        instructions=WELCOME_MESSAGE.strip()
    )

    @session.on("user_message")
    def on_user_message(message):
        asyncio.create_task(assistant.on_message(_format_message(message)))

    @session.on("function_call")
    def on_function_call(function_call):
        async def handle_call():
            name = function_call.get("name", "")
            arguments = function_call.get("arguments", {})
            logger.info(f"Function called: {name} with arguments: {arguments}")
            result = await assistant.process_function_call(name, **arguments)
            await session.send_function_result(function_call["id"], result)

        asyncio.create_task(handle_call())


if __name__ == "__main__":
    logger.info("Starting LiveKit agent application")
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
