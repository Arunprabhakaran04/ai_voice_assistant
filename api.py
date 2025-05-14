from livekit.agents import Agent
import enum
from typing import Annotated, Optional
import logging
from db_driver import DatabaseDriver

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()

class CarDetails(enum.Enum):
    VIN = "vin"
    Make = "make"
    Model = "model"
    Year = "year"
    

class AssistantFnc:
    def __init__(self):
        self._car_details = {
            CarDetails.VIN: "",
            CarDetails.Make: "",
            CarDetails.Model: "",
            CarDetails.Year: ""
        }
    
    def get_car_str(self):
        car_str = ""
        for key, value in self._car_details.items():
            car_str += f"{key.name}: {value}\n"
            
        return car_str
    
    def lookup_car(self, vin: str):
        """Lookup a car by its VIN"""
        logger.info("lookup car - vin: %s", vin)
        
        result = DB.get_car_by_vin(vin)
        if result is None:
            return "Car not found"
        
        self._car_details = {
            CarDetails.VIN: result.vin,
            CarDetails.Make: result.make,
            CarDetails.Model: result.model,
            CarDetails.Year: result.year
        }
        
        return f"The car details are: {self.get_car_str()}"
    
    def get_car_details(self):
        """Get the details of the current car"""
        logger.info("get car details")
        return f"The car details are: {self.get_car_str()}"
    
    def create_car(self, vin: str, make: str, model: str, year: int):
        """Create a new car"""
        logger.info("create car - vin: %s, make: %s, model: %s, year: %s", vin, make, model, year)
        result = DB.create_car(vin, make, model, year)
        if result is None:
            return "Failed to create car"
        
        self._car_details = {
            CarDetails.VIN: result.vin,
            CarDetails.Make: result.make,
            CarDetails.Model: result.model,
            CarDetails.Year: result.year
        }
        
        return "car created!"
    
    def has_car(self):
        """Check if a car profile exists"""
        return self._car_details[CarDetails.VIN] != ""