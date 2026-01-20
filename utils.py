from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Vehicle, Log
from datetime import date, timedelta
import pandas as pd

DB_FILE = 'sqlite:///app.db'
engine = create_engine(DB_FILE, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()

def get_users():
    session = get_db_session()
    users = session.query(User).all()
    session.close()
    return users

def get_vehicles():
    session = get_db_session()
    vehicles = session.query(Vehicle).all()
    session.close()
    return vehicles

def create_log(log_data):
    session = get_db_session()
    new_log = Log(**log_data)
    session.add(new_log)
    session.commit()
    session.close()

def get_logs(filters=None):
    session = get_db_session()
    query = session.query(Log)
    
    if filters:
        # Implement filters if needed
        pass
        
    logs = query.all()
    session.close()
    return logs

def get_logs_as_dataframe():
    session = get_db_session()
    query = session.query(
        Log.date,
        User.name.label('user_name'),
        Vehicle.name.label('vehicle_name'),
        Log.start_time,
        Log.end_time,
        Log.start_km,
        Log.end_km,
        Log.refuel_check,
        Log.alcohol_check,
        Log.tire_check
    ).join(User).join(Vehicle)
    
    df = pd.read_sql(query.statement, session.bind)
    session.close()
    return df

def create_vehicle(vehicle_data):
    session = get_db_session()
    new_vehicle = Vehicle(**vehicle_data)
    session.add(new_vehicle)
    session.commit()
    session.close()

def update_vehicle(vehicle_id, vehicle_data):
    session = get_db_session()
    vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle:
        for key, value in vehicle_data.items():
            setattr(vehicle, key, value)
        session.commit()
    session.close()

def get_last_km(vehicle_id):
    session = get_db_session()
    last_log = session.query(Log).filter(Log.vehicle_id == vehicle_id).order_by(Log.date.desc(), Log.id.desc()).first()
    session.close()
    if last_log:
        return last_log.end_km
    return 0.0

def check_alerts():
    session = get_db_session()
    vehicles = session.query(Vehicle).all()
    alerts = []
    
    today = date.today()
    
    for v in vehicles:
        # Inspection Alert
        if v.next_inspection_date:
            days_until = (v.next_inspection_date - today).days
            if 0 <= days_until <= 30:
                alerts.append(f"⚠️ 【車検】 {v.name} ({v.plate_number}) の車検が {days_until} 日後に迫っています ({v.next_inspection_date})")
            elif days_until < 0:
                alerts.append(f"🚨 【車検切れ】 {v.name} ({v.plate_number}) の車検が切れています！ ({v.next_inspection_date})")

        # Oil Change Alert
        last_km = get_last_km(v.id)
        if last_km - v.last_oil_change_km > 5000:
             alerts.append(f"⚠️ 【オイル交換】 {v.name} ({v.plate_number}) は前回の交換から {last_km - v.last_oil_change_km:.1f}km 走行しています (目安: 5000km)")

    session.close()
    return alerts
