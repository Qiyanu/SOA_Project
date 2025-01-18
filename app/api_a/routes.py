from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Client
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

@router.post(
    "/register",
    summary="Register a new user",
    description="Register a new user with a unique username and password."
)
def register_user(
    username: str = Query(..., description="The desired username (must be unique)."),
    password: str = Query(..., description="The desired password."),
    db: Session = Depends(get_db),
):
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
def authenticate_user(
    username: str = Query(..., description="The username to log in."),
    password: str = Query(..., description="The password to log in."),
    db: Session = Depends(get_db),
):
    """
    Authenticate a user.

    - **username**: The username to log in.
    - **password**: The password to log in.
    """
    # Retrieve the user by username
    existing_user = db.query(Client).filter(Client.username == username).first()
    if not existing_user or not pwd_context.verify(password, existing_user.password):
        raise HTTPException(status_code=401, detail="Error: Invalid username or password.")

    return {"message": f"Authentication successful for user: {username}"}
