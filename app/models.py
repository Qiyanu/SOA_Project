from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Train(Base):
    __tablename__ = "trains"

    train_id = Column(Integer, primary_key=True, autoincrement=True)
    departure_station = Column(String, nullable=False)
    arrival_station = Column(String, nullable=False)
    departure_datetime = Column(DateTime, nullable=False)
    arrival_datetime = Column(DateTime, nullable=False)

    # One-to-Many relationship with seats
    seats = relationship("Seat", back_populates="train")


class Seat(Base):
    __tablename__ = "seats"

    seat_id = Column(Integer, primary_key=True, autoincrement=True)
    train_id = Column(Integer, ForeignKey("trains.train_id"), nullable=False)
    seat_class = Column(String, nullable=False)  # Changed Enum to String
    status = Column(String, nullable=False, default="Available")  # Changed Enum to String
    fare = Column(Float, nullable=False)  # Added fare for each seat

    # Many-to-One relationship with Train
    train = relationship("Train", back_populates="seats")

    # One-to-One relationship with Reservation
    reservation = relationship("Reservation", back_populates="seat", uselist=False)


class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # One-to-Many relationship with Reservations
    reservations = relationship("Reservation", back_populates="client")


class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.seat_id"), nullable=False)
    ticket_type = Column(String, nullable=False, default="Flexible")  # Changed Enum to String
    status = Column(String, nullable=False, default="Confirmed")  # Changed Enum to String

    # Many-to-One relationship with Client
    client = relationship("Client", back_populates="reservations")

    # One-to-One relationship with Seat
    seat = relationship("Seat", back_populates="reservation")
