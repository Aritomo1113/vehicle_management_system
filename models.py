from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin' or 'staff'

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    plate_number = Column(String, nullable=False)
    next_inspection_date = Column(Date, nullable=True)
    last_oil_change_km = Column(Float, default=0.0)

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    start_km = Column(Float, nullable=True)
    end_km = Column(Float, nullable=True)
    alcohol_check = Column(Boolean, default=False)
    tire_check = Column(Boolean, default=False)
    refuel_check = Column(Boolean, default=False)

    user = relationship("User")
    vehicle = relationship("Vehicle")
