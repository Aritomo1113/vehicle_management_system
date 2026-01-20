from utils import init_db, get_db_session, User, Vehicle
from datetime import date

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

    session.commit()
    session.close()
    print("Database initialized and seeded.")

if __name__ == "__main__":
    seed_data()
