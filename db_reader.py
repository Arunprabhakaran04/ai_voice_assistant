import sqlite3

def read_all_cars(db_path="assistant.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT vin, make, model, year FROM cars")
        rows = cursor.fetchall()

        if not rows:
            print("No cars found in the database.")
            return []

        print("Cars in database:")
        for row in rows:
            print(f"VIN: {row[0]}, Make: {row[1]}, Model: {row[2]}, Year: {row[3]}")

        return rows
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

if __name__ == "__main__":
    read_all_cars("main\\auto_db.sqlite")