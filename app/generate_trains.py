from sqlalchemy.orm import Session
from app.models import Train, Seat
from datetime import datetime, timedelta
import random

def generate_random_trains_and_seats(db: Session, num_trains: int = 100, min_seats: int = 5, max_seats: int = 50):
    stations = ["StationA", "StationB", "StationC", "StationD", "StationE", "StationF"]
    seat_classes = ["First", "Business", "Standard"]

    total_seats = 0  # Initialize total seats counter

    for _ in range(num_trains):
        # Generate random departure and arrival stations
        departure_station, arrival_station = random.sample(stations, 2)

        # Generate random departure and arrival times rounded to the nearest minute
        departure_datetime = (datetime.now() + timedelta(days=random.randint(1, 30), hours=random.randint(1, 12))).replace(second=0, microsecond=0)
        arrival_datetime = (departure_datetime + timedelta(hours=random.randint(1, 5))).replace(second=0, microsecond=0)

        # Create a train
        train = Train(
            departure_station=departure_station,
            arrival_station=arrival_station,
            departure_datetime=departure_datetime,
            arrival_datetime=arrival_datetime,
        )
        db.add(train)
        db.commit()

        # Generate a random number of seats for the train
        num_seats = random.randint(min_seats, max_seats)
        total_seats += num_seats  # Add to total seats counter

        # Define base fares for each class to ensure order
        base_fares = {
            "First": random.uniform(200, 300),
            "Business": random.uniform(100, 199),
            "Standard": random.uniform(50, 99)
        }

        # Create seats for the train
        for _ in range(num_seats):
            seat_class = random.choice(seat_classes)
            fare = round(base_fares[seat_class], 2)  # Assign fare based on class
            seat = Seat(
                train_id=train.train_id,
                seat_class=seat_class,
                status="Available",
                fare=fare,
            )
            db.add(seat)

        db.commit()

    print(f"Generated {num_trains} trains with a random number of seats between {min_seats} and {max_seats} per train.")
    print(f"Total seats generated: {total_seats}")
