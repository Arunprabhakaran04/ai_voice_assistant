from livekit.agents import Agent, function_tool, RunContext
from api import lookup_car, create_car, get_car_details
import logging
from prompts import WELCOME_MESSAGE

logger = logging.getLogger("livekit-agent")

class GreetingAgent(Agent):
    def __init__(self):
        super().__init__(instructions="Welcome the user and ask for their VIN or if they want to create a new account.")

    async def on_enter(self):
        await self.session.say(WELCOME_MESSAGE)

    @function_tool()
    async def handle_user_response(self, context: RunContext, response: str):
        """
        Determine if the user has provided a VIN or wants to create a new account.
        - If the user provides a VIN, call this function to look up their car details.
        - If the user wants to create a new account, call this function to initiate the registration process.
        """
        if "vin" in response.lower():
            return await lookup_car(context, vin=response)
        else:
            return RegistrationAgent()

class RegistrationAgent(Agent):
    def __init__(self):
        super().__init__(instructions="Ask for car make, model, year, and VIN. Call the tool to register only once.")

    async def on_enter(self):
        await self.session.say("Let's get started with creating your account. Please provide your car's make, model, year, and VIN.")

    @function_tool()
    async def collect_car_details(self, context: RunContext, make: str, model: str, year: int, vin: str):
        """
        Collect the car's make, model, year, and VIN from the user.
        Use this information to create a new account in the database.
        Ensure this function is called only once after collecting all details.
        """
        return await create_car(context, make=make, model=model, year=year, vin=vin)

class ServiceAgent(Agent):
    def __init__(self):
        super().__init__(instructions="Assist the user with their car-related queries.")

    async def on_enter(self):
        await self.session.say("How can I assist you with your car today?")

    @function_tool()
    async def handle_query(self, context: RunContext, query: str):
        """
        Handle user queries related to their car.
        Retrieve and provide car details based on the user's request.
        """
        return await get_car_details(context)

