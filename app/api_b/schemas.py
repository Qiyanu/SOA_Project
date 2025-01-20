from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


# Schema for seat information
class SeatResponse(BaseModel):
    seat_id: int
    train_id: int  
    seat_class: str
    fare: float
    status: str

    class Config:
        from_attributes = True  # Allow ORM mapping


# Schema for train filtering request
class TrainFilterRequest(BaseModel):
    departure_station: str
    arrival_station: str
    outbound_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    min_available_seats: Optional[int] = None
    seat_class: Optional[str] = None


# Schema for train response
class TrainResponse(BaseModel):
    train_id: int
    departure_station: str
    arrival_station: str
    departure_date: datetime
    arrival_date: datetime
    available_seats_first: int
    available_seats_business: int
    available_seats_standard: int

    class Config:
        from_attributes = True  # Allow ORM mapping


# Schema for grouped seats response
class GroupedSeatsResponse(BaseModel):
    train_id: int
    seats: Dict[str, List[SeatResponse]]  # Seats grouped by class

    class Config:
        from_attributes = True  # Allow ORM mapping


# Schema for reservation response
class ReservationResponse(BaseModel):
    reservation_id: int
    client_id: int
    seat_id: int
    train_id: int
    ticket_type: str
    status: str

    class Config:
        from_attributes = True  # Allow ORM mapping
