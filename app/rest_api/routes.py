from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Train, Seat, Client, Reservation
from app.rest_api.schemas import TrainResponse, GroupedSeatsResponse, SeatResponse, ReservationResponse
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.get(
    "/trains/filter",
    response_model=List[TrainResponse],
    summary="Filter available trains",
    description="Filters and retrieves trains with available seats based on departure/arrival stations, travel dates, seat class, and number of tickets."
)
def filter_trains(
    departure_station: str = Query(..., description="Departure station name."),
    arrival_station: str = Query(..., description="Arrival station name."),
    outbound_date: Optional[datetime] = Query(None, description="Outbound travel date (optional)."),
    return_date: Optional[datetime] = Query(None, description="Return travel date (optional)."),
    min_available_seats: Optional[int] = Query(None, description="Minimum number of available seats required (optional)."),
    seat_class: Optional[str] = Query(None, description="Seat class: First, Business, or Standard (optional)."),
    db: Session = Depends(get_db),
):
    """
    Filters and returns available trains based on criteria such as:
    - Departure/arrival stations
    - Outbound/return dates
    - Number of seats
    - Seat class (First, Business, or Standard)

    The response includes train details and the number of available seats per class.
    """
    query = db.query(
        Train,
        func.count(Seat.seat_id).label("available_seats")
    ).join(Seat).filter(
        Train.departure_station == departure_station,
        Train.arrival_station == arrival_station,
        Seat.status == "Available"
    )

    if outbound_date:
        query = query.filter(Train.departure_datetime >= outbound_date)

    if return_date:
        query = query.filter(Train.departure_datetime <= return_date)

    if seat_class:
        query = query.filter(Seat.seat_class == seat_class)

    query = query.group_by(Train.train_id)

    if min_available_seats:
        query = query.having(func.count(Seat.seat_id) >= min_available_seats)

    trains = query.all()

    if not trains:
        raise HTTPException(status_code=404, detail="No available trains found.")

    result = []
    for train, available_seats in trains:
        available_seat_counts = {
            "First": sum(1 for seat in train.seats if seat.seat_class == "First" and seat.status == "Available"),
            "Business": sum(1 for seat in train.seats if seat.seat_class == "Business" and seat.status == "Available"),
            "Standard": sum(1 for seat in train.seats if seat.seat_class == "Standard" and seat.status == "Available"),
        }

        result.append(TrainResponse(
            train_id=train.train_id,
            departure_station=train.departure_station,
            arrival_station=train.arrival_station,
            departure_date=train.departure_datetime,
            arrival_date=train.arrival_datetime,
            available_seats_first=available_seat_counts["First"],
            available_seats_business=available_seat_counts["Business"],
            available_seats_standard=available_seat_counts["Standard"]
        ))

    return result

@router.get(
    "/trains/{train_id}/seats",
    response_model=GroupedSeatsResponse,
    summary="Get seats of a train",
    description="Returns the available seats of a train grouped by class and sorted by price (high to low). Optionally, filter by class.",
)
def get_train_seats(
    train_id: int,
    seat_class: Optional[str] = Query(None, description="Filter seats by class: First, Business, or Standard (optional)."),
    db: Session = Depends(get_db),
):
    """
    Returns the available seats of a train grouped by class and sorted by price (high to low).
    Optionally, filter by class.
    """
    # Query for available seats only
    query = db.query(Seat).filter(
        Seat.train_id == train_id,
        Seat.status == "Available"  # Ensure only available seats are included
    )

    # Apply seat class filter if specified
    if seat_class:
        query = query.filter(Seat.seat_class == seat_class)

    # Fetch and order seats by fare (high to low)
    seats = query.order_by(Seat.fare.desc()).all()

    if not seats:
        raise HTTPException(status_code=404, detail="No available seats found for the specified train.")

    # Serialize seats into SeatResponse
    serialized_seats = [
        SeatResponse(
            seat_id=seat.seat_id,
            train_id=seat.train_id,  # Explicitly include train_id
            seat_class=seat.seat_class,
            fare=seat.fare,
            status=seat.status,
        )
        for seat in seats
    ]

    # Group seats by class
    grouped_seats = {
        "First": [seat for seat in serialized_seats if seat.seat_class == "First"],
        "Business": [seat for seat in serialized_seats if seat.seat_class == "Business"],
        "Standard": [seat for seat in serialized_seats if seat.seat_class == "Standard"],
    }

    # Construct the response
    if seat_class:
        result = {
            "train_id": train_id,
            "seats": {seat_class: grouped_seats.get(seat_class, [])},  # Return only the filtered class
        }
    else:
        result = {
            "train_id": train_id,
            "seats": grouped_seats,  # Return all classes grouped
        }

    return result

@router.get(
    "/seats/{seat_id}",
    summary="Get seat details",
    description="Retrieve the details of a specific seat by its ID."
)
def get_seat(seat_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the details of a specific seat by its ID.
    """
    # Query the seat by ID
    seat = db.query(Seat).filter(Seat.seat_id == seat_id).first()

    # Raise an exception if the seat is not found
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found.")

    # Return the seat details along with the train ID
    return {
        "seat_id": seat.seat_id,
        "train_id": seat.train_id,
        "seat_class": seat.seat_class,
        "fare": seat.fare,
        "status": seat.status,
    }

@router.get(
    "/trains/{train_id}",
    summary="Get train details",
    description="Retrieve the details of a specific train by its ID.",
)
def get_train(train_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the details of a specific train by its ID.
    """
    # Query the train by ID
    train = db.query(Train).filter(Train.train_id == train_id).first()

    # Raise an exception if the train is not found
    if not train:
        raise HTTPException(status_code=404, detail="Train not found.")

    # Return the train details
    return {
        "train_id": train.train_id,
        "departure_station": train.departure_station,
        "arrival_station": train.arrival_station,
        "departure_datetime": train.departure_datetime,
        "arrival_datetime": train.arrival_datetime,
    }

@router.post(
    "/reservations",
    response_model=ReservationResponse,  # Use the new schema
    summary="Create a reservation",
    description="Create a reservation for a specific seat and update the seat's status to 'Reserved'."
)
def create_reservation(
    client_id: int,
    seat_id: int,
    ticket_type: str = Query(..., description="Type of ticket: Flexible or NonFlexible."),
    db: Session = Depends(get_db),
):
    # Validate ticket_type
    if ticket_type not in ["Flexible", "NonFlexible"]:
        raise HTTPException(status_code=400, detail="Invalid ticket type. Must be 'Flexible' or 'NonFlexible'.")

    # Check if client exists
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")

    # Query the seat to ensure it exists and is available
    seat = db.query(Seat).filter(Seat.seat_id == seat_id, Seat.status == "Available").first()
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found or already reserved.")

    # Create the reservation
    reservation = Reservation(
        client_id=client_id,
        seat_id=seat_id,
        ticket_type=ticket_type,
        status="Confirmed",
    )
    db.add(reservation)

    # Update the seat's status to 'Reserved'
    seat.status = "Reserved"
    db.commit()

    # Return the reservation details
    return ReservationResponse(
        reservation_id=reservation.reservation_id,
        client_id=reservation.client_id,
        seat_id=reservation.seat_id,
        train_id=seat.train_id,
        ticket_type=reservation.ticket_type,
        status=reservation.status,
    )

@router.get(
    "/clients/{client_id}/reservations",
    summary="Get a client's reservations",
    description="Retrieve all reservations made by a specific client with an optional filter for reservation status.",
)
def get_client_reservations(
    client_id: int,
    reservation_status: Optional[str] = Query(
        None, description="Filter reservations by status (e.g., 'Confirmed', 'Cancelled')."
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve all reservations made by a specific client with an optional filter for reservation status.
    """
    # Query the client to ensure they exist
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")

    # Base query to fetch all reservations for the client
    query = db.query(Reservation).filter(Reservation.client_id == client_id)

    # Apply reservation status filter if provided
    if reservation_status:
        query = query.filter(Reservation.status == reservation_status)

    # Fetch reservations
    reservations = query.all()

    if not reservations:
        raise HTTPException(status_code=404, detail="No reservations found for the specified client.")

    # Return the reservations as a list of dictionaries
    result = []
    for reservation in reservations:
        seat = db.query(Seat).filter(Seat.seat_id == reservation.seat_id).first()
        result.append({
            "reservation_id": reservation.reservation_id,
            "seat_id": reservation.seat_id,
            "train_id": seat.train_id if seat else None,
            "ticket_type": reservation.ticket_type,
            "status": reservation.status,
        })

    return result

@router.put(
    "/reservations/{reservation_id}/cancel",
    summary="Cancel a reservation",
    description="Cancel a reservation.",
)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    """
    Cancel a reservation.
    """
    # Query the reservation to ensure it exists
    reservation = db.query(Reservation).filter(Reservation.reservation_id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found.")

    # Check if the reservation is already cancelled
    if reservation.status == "Cancelled":
        raise HTTPException(status_code=400, detail="Reservation is already cancelled.")

    # Query the seat associated with the reservation
    seat = db.query(Seat).filter(Seat.seat_id == reservation.seat_id).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Associated seat not found.")

    # Update the reservation and seat statuses
    reservation.status = "Cancelled"
    seat.status = "Available"

    db.commit()

    # Return the updated reservation details
    return {
        "reservation_id": reservation.reservation_id,
        "client_id": reservation.client_id,
        "seat_id": reservation.seat_id,
        "train_id": seat.train_id,
        "ticket_type": reservation.ticket_type,
        "status": reservation.status,
    }
