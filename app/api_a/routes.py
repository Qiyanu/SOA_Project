from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import requests
from app.database import get_db
from app.models import Client
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

API_B_BASE_URL = "http://127.0.0.1:8001"  # Base URL for API B


@router.post(
    "/register",
    summary="Register a new user",
    description="Register a new user with a unique username and password."
)
def register_user(username: str, password: str, db=Depends(get_db)):
    """
    Register a new user.

    - **username**: The desired username (must be unique).
    - **password**: The desired password.
    """
    # Check if the username already exists
    existing_user = db.query(Client).filter(Client.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Error: Username already exists.")

    # Hash the password
    hashed_password = pwd_context.hash(password)

    # Create a new user
    new_user = Client(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully."}


@router.post(
    "/authenticate",
    summary="Authenticate a user",
    description="Authenticate a user with a username and password."
)
def authenticate_user(username: str, password: str, db=Depends(get_db)):
    """
    Authenticate a user.

    - **username**: The username to log in.
    - **password**: The password to log in.
    """
    existing_user = db.query(Client).filter(Client.username == username).first()
    if not existing_user or not pwd_context.verify(password, existing_user.password):
        raise HTTPException(status_code=401, detail="Error: Invalid username or password.")

    return {"message": f"Authentication successful for user: {username}"}


@router.get(
    "/trains/filter",
    summary="Filter available trains",
    description="Filters available trains using the API B service.",
)
def filter_trains(
    departure_station: str = Query(..., description="Departure station name."),
    arrival_station: str = Query(..., description="Arrival station name."),
    outbound_date: Optional[datetime] = Query(None, description="Outbound travel date (optional)."),
    return_date: Optional[datetime] = Query(None, description="Return travel date (optional)."),
    min_available_seats: Optional[int] = Query(None, description="Minimum number of available seats required (optional)."),
    seat_class: Optional[str] = Query(None, description="Seat class: First, Business, or Standard (optional)."),
):
    """
    Filters available trains using the API B service.

    - **departure_station**: Departure station name.
    - **arrival_station**: Arrival station name.
    - **outbound_date**: Outbound travel date (optional).
    - **return_date**: Return travel date (optional).
    - **min_available_seats**: Minimum number of available seats required (optional).
    - **seat_class**: Seat class: First, Business, or Standard (optional).
    """
    # Construct query parameters
    params = {
        "departure_station": departure_station,
        "arrival_station": arrival_station,
        "outbound_date": outbound_date.isoformat() if outbound_date else None,
        "return_date": return_date.isoformat() if return_date else None,
        "min_available_seats": min_available_seats,
        "seat_class": seat_class,
    }

    # Call API B
    response = requests.get(f"{API_B_BASE_URL}/trains/filter", params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()



@router.get(
    "/trains/{train_id}",
    summary="Get train details",
    description="Retrieve the details of a specific train using the API B service."
)
def get_train(train_id: int):
    """
    Retrieve train details using the API B service.
    """
    response = requests.get(f"{API_B_BASE_URL}/trains/{train_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()


@router.get(
    "/trains/{train_id}/seats",
    summary="Get train seats",
    description="Retrieve seats for a specific train using the API B service."
)
def get_train_seats(train_id: int):
    """
    Retrieve train seats using the API B service.
    """
    response = requests.get(f"{API_B_BASE_URL}/trains/{train_id}/seats")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()

@router.get(
    "/seats/{seat_id}",
    summary="Get seat details",
    description="Retrieve the details of a specific seat using the API B service."
)
def get_seat_details(seat_id: int):
    """
    Retrieve the details of a specific seat using the API B service.

    - **seat_id**: The ID of the seat to retrieve details for.
    """
    response = requests.get(f"{API_B_BASE_URL}/seats/{seat_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()

@router.post(
    "/reservations",
    summary="Create a reservation",
    description="Create a reservation using the API B service."
)
def create_reservation(client_id: int, seat_id: int, ticket_type: str):
    """
    Create a reservation using the API B service.
    """
    data = {"client_id": client_id, "seat_id": seat_id, "ticket_type": ticket_type}
    response = requests.post(f"{API_B_BASE_URL}/reservations", json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()


@router.get(
    "/clients/{client_id}/reservations",
    summary="Get client reservations",
    description="Retrieve reservations for a client using the API B service."
)
def get_client_reservations(client_id: int):
    """
    Retrieve client reservations using the API B service.
    """
    response = requests.get(f"{API_B_BASE_URL}/clients/{client_id}/reservations")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()

@router.put(
    "/reservations/{reservation_id}/cancel",
    summary="Cancel a reservation",
    description="Cancel a reservation by updating its status to 'Cancelled' and the corresponding seat status to 'Available' using the API B service."
)
def cancel_reservation(reservation_id: int):
    """
    Cancel a reservation using the API B service.

    - **reservation_id**: The ID of the reservation to cancel.
    """
    response = requests.put(f"{API_B_BASE_URL}/reservations/{reservation_id}/cancel")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()
