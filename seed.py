from utils import init_db, get_db_session, User, Vehicle, Log
from datetime import date
from datetime import time

def seed_data():
    init_db()
    session = get_db_session()

    # Check if data exists
    if session.query(User).first():
        print("Data already exists. Skipping seed.")
        session.close()
        return

    # Add Users
    users = [
        User(name="管理者太郎", role="admin"),
        User(name="看護師花子", role="staff"),
        User(name="看護師次郎", role="staff"),
    ]
    session.add_all(users)

    # Add Vehicles
    vehicles = [
        Vehicle(name="プリウス", plate_number="品川 500 あ 1234", next_inspection_date=date(2025, 12, 1), last_oil_change_km=10000.0),
        Vehicle(name="N-BOX", plate_number="品川 580 い 5678", next_inspection_date=date(2024, 2, 1), last_oil_change_km=5000.0), # Alert candidate
        Vehicle(name="アクア", plate_number="品川 500 う 9012", next_inspection_date=date(2026, 1, 15), last_oil_change_km=20000.0),
    ]
    session.add_all(vehicles)

    # Add sample Logs
    # Map created users/vehicles by index (they will get ids after flush/commit)
    session.commit()

    users = session.query(User).all()
    vehicles = session.query(Vehicle).all()

    # Create a few sample logs including air_pressure_check variations
    sample_logs = [
        Log(
            user_id=users[1].id,
            vehicle_id=vehicles[0].id,
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 30),
            start_km=10000.0,
            end_km=10045.5,
            alcohol_check=False,
            tire_check=True,
            refuel_check=False,
            air_pressure_check=True,
            oil_change_check=False
        ),
        Log(
            user_id=users[2].id,
            vehicle_id=vehicles[1].id,
            date=date.today(),
            start_time=time(8, 30),
            end_time=time(16, 0),
            start_km=5000.0,
            end_km=5055.0,
            alcohol_check=False,
            tire_check=False,
            refuel_check=True,
            air_pressure_check=False,
            oil_change_check=True
        ),
    ]

    session.add_all(sample_logs)

    session.commit()
    session.close()
    print("Database initialized and seeded.")

if __name__ == "__main__":
    seed_data()
