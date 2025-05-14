# api.py
from livekit.agents import function_tool, RunContext
from db_driver import DatabaseDriver

DB = DatabaseDriver()

@function_tool()
async def lookup_car(context: RunContext, vin: str):
    car = DB.get_car_by_vin(vin)
    if car:
        return f"Car found: {car.make} {car.model}, {car.year}"
    else:
        return "Car not found."

@function_tool()
async def create_car(context: RunContext, make: str, model: str, year: int, vin: str):
    car = DB.create_car(vin, make, model, year)
    return f"Car created: {car.make} {car.model}, {car.year}"

@function_tool()
async def get_car_details(context: RunContext):
    # Implement logic to retrieve car details based on context
    pass
