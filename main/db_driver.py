# db_driver.py
import sqlite3
from dataclasses import dataclass

@dataclass
class Car:
    vin: str
    make: str
    model: str
    year: int

class DatabaseDriver:
    def __init__(self, db_path: str = "auto_db.sqlite"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cars (
                    vin TEXT PRIMARY KEY,
                    make TEXT NOT NULL,
                    model TEXT NOT NULL,
                    year INTEGER NOT NULL
                )
            """)
            conn.commit()

    def create_car(self, vin: str, make: str, model: str, year: int) -> Car:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cars (vin, make, model, year) VALUES (?, ?, ?, ?)",
                (vin, make, model, year)
            )
            conn.commit()
            return Car(vin=vin, make=make, model=model, year=year)

    def get_car_by_vin(self, vin: str) -> Car:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cars WHERE vin = ?", (vin,))
            row = cursor.fetchone()
            if row:
                return Car(vin=row[0], make=row[1], model=row[2], year=row[3])
            return None
