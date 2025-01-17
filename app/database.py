from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Client
from app.generate_trains import generate_random_trains_and_seats

DATABASE_URL = "sqlite:///train_booking.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def initialize_database():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed data
    session = SessionLocal()

    # Add a sample client
    client1 = Client(username="testuser", password="password123")
    session.add(client1)
    session.commit()

    # Generate random trains and seats
    generate_random_trains_and_seats(session, num_trains=100, min_seats = 5, max_seats = 50)

    session.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    initialize_database()
