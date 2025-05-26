#!/usr/bin/env python3.11
import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker()

# Configuration
NUM_LOCATIONS = 40
NUM_PASSENGERS = 50
NUM_EMPLOYEES = 15 # Fewer employees
NUM_ACCOMMODATIONS = 60
NUM_FLIGHTS = 70
NUM_CAR_RENTALS = 50
NUM_CRUISES = 30
NUM_BOOKINGS = 80
AVG_PASSENGERS_PER_BOOKING = 2.5
AVG_ACCOMMODATIONS_PER_BOOKING = 0.8
AVG_TRANSPORTS_PER_BOOKING = 1.2
AVG_PAYMENTS_PER_BOOKING = 1.1
AVG_REVIEWS_PER_BOOKING = 0.7

# Database file path
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "travel_agency.db")
output_sql_path = os.path.join(os.path.dirname(__file__), "sql", "populate_data.sql")

# Ensure the sql directory exists
os.makedirs(os.path.dirname(output_sql_path), exist_ok=True)

# Data storage
locations = []
passengers = []
employees = []
accommodations = []
flights = []
car_rentals = []
cruises = []
bookings = []
booking_passengers = []
booking_accommodations = []
booking_transportations = []
payments = []
reviews = []

# --- Data Generation Functions ---

def generate_locations(n):
    for _ in range(n):
        city = fake.city()
        country = fake.country()
        state = fake.state() if country == "United States" else None
        locations.append((city, state, country))

def generate_passengers(n):
    for _ in range(n):
        name = fake.name()
        gender = random.choice(["Male", "Female", "Other"])
        age = random.randint(18, 80)
        email = fake.unique.email()
        phone = fake.phone_number()
        passengers.append((name, gender, age, email, phone))

def generate_employees(n):
    # Generate initial employees without supervisor
    for i in range(n):
        name = fake.name()
        role = random.choice(["Agent", "Manager", "Admin", "Support"])
        join_date = fake.date_between(start_date="-5y", end_date="today").isoformat()
        employees.append((name, role, join_date, None)) # SupervisorID initially None

def generate_accommodations(n):
    if not locations:
        print("Error: Need locations to generate accommodations.")
        return
    location_ids = list(range(1, len(locations) + 1))
    for _ in range(n):
        name = fake.company() + " " + random.choice(["Hotel", "Resort", "Inn", "Suites"])
        acc_type = random.choice(["Hotel", "Hostel", "Resort", "Airbnb", "Guesthouse"])
        rate = round(random.uniform(50, 500), 2)
        facilities = ", ".join(fake.words(nb=random.randint(3, 7)))
        discount = round(random.choice([0.0, 0.05, 0.1, 0.15, 0.2]), 2)
        location_id = random.choice(location_ids)
        accommodations.append((name, acc_type, rate, facilities, discount, location_id))

def generate_flights(n):
    if not locations:
        print("Error: Need locations to generate flights.")
        return
    location_ids = list(range(1, len(locations) + 1))
    carriers = [fake.company() + " Airlines" for _ in range(10)]
    for _ in range(n):
        flight_number = fake.bothify(text="??####", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        carrier = random.choice(carriers)
        source_id, dest_id = random.sample(location_ids, 2)
        departure_dt = fake.date_time_between(start_date="+1d", end_date="+1y")
        duration = timedelta(hours=random.uniform(1, 15))
        arrival_dt = departure_dt + duration
        flight_class = random.choice(["Economy", "Business", "First"])
        fare = round(random.uniform(100, 2000), 2)
        flights.append((flight_number, carrier, source_id, dest_id, departure_dt.isoformat(), arrival_dt.isoformat(), flight_class, fare))

def generate_car_rentals(n):
    if not locations:
        print("Error: Need locations to generate car rentals.")
        return
    location_ids = list(range(1, len(locations) + 1))
    companies = [fake.company() + " Rentals" for _ in range(8)]
    car_types = ["Sedan", "SUV", "Convertible", "Van", "Truck", "Compact"]
    for _ in range(n):
        company = random.choice(companies)
        car_type = random.choice(car_types)
        pickup_loc_id = random.choice(location_ids)
        dropoff_loc_id = random.choice(location_ids) # Can be same or different
        pickup_dt = fake.date_time_between(start_date="+1d", end_date="+1y")
        rental_days = random.randint(1, 14)
        dropoff_dt = pickup_dt + timedelta(days=rental_days)
        rent = round(random.uniform(30, 150) * rental_days, 2)
        car_rentals.append((company, car_type, pickup_loc_id, dropoff_loc_id, pickup_dt.isoformat(), dropoff_dt.isoformat(), rent))

def generate_cruises(n):
    if not locations:
        print("Error: Need locations to generate cruises.")
        return
    location_ids = list(range(1, len(locations) + 1))
    lines = [fake.company() + " Cruises" for _ in range(5)]
    for _ in range(n):
        cruise_name = random.choice(["Caribbean Explorer", "Mediterranean Dream", "Alaskan Wonder", "Pacific Paradise", "European Voyage"])
        line = random.choice(lines)
        source_id, dest_id = random.sample(location_ids, 2)
        departure_date = fake.date_between(start_date="+1m", end_date="+2y")
        duration_days = random.randint(5, 21)
        return_date = departure_date + timedelta(days=duration_days)
        fare = round(random.uniform(500, 5000), 2)
        cruises.append((cruise_name, line, source_id, dest_id, departure_date.isoformat(), return_date.isoformat(), fare))

def generate_bookings(n):
    if not employees:
        print("Error: Need employees to generate bookings.")
        return
    employee_ids = list(range(1, len(employees) + 1))
    for _ in range(n):
        group_name = fake.catch_phrase() + " Trip" if random.random() > 0.3 else None
        purpose = random.choice(["Leisure", "Business", "Honeymoon", "Family Vacation", "Adventure"])
        booking_date = fake.date_between(start_date="-1y", end_date="today").isoformat()
        employee_id = random.choice(employee_ids) if random.random() > 0.1 else None # Some bookings might not have an assigned employee
        # TotalCost will be calculated later or set approximately
        total_cost = round(random.uniform(200, 10000), 2)
        bookings.append((group_name, purpose, booking_date, employee_id, total_cost))

def generate_booking_passengers():
    if not bookings or not passengers:
        print("Error: Need bookings and passengers.")
        return
    booking_ids = list(range(1, len(bookings) + 1))
    passenger_ids = list(range(1, len(passengers) + 1))
    for booking_id in booking_ids:
        num_pass = max(1, int(random.gauss(AVG_PASSENGERS_PER_BOOKING, 1)))
        selected_passengers = random.sample(passenger_ids, min(num_pass, len(passenger_ids)))
        for passenger_id in selected_passengers:
            if (booking_id, passenger_id) not in booking_passengers:
                 booking_passengers.append((booking_id, passenger_id))

def generate_booking_accommodations():
    if not bookings or not accommodations:
        print("Error: Need bookings and accommodations.")
        return
    booking_ids = list(range(1, len(bookings) + 1))
    accommodation_ids = list(range(1, len(accommodations) + 1))
    for booking_id in booking_ids:
        if random.random() < AVG_ACCOMMODATIONS_PER_BOOKING:
            num_acc = random.randint(1, 2)
            selected_accs = random.sample(accommodation_ids, min(num_acc, len(accommodation_ids)))
            for acc_id in selected_accs:
                # Find related accommodation to get rate for cost calculation
                # In a real scenario, connect to DB or use stored data
                # Here, we estimate cost based on typical rates
                check_in_date = fake.date_between(start_date="+1d", end_date="+1y")
                duration = random.randint(2, 14)
                check_out_date = check_in_date + timedelta(days=duration)
                cost = round(random.uniform(50, 500) * duration, 2) # Estimated cost
                booking_accommodations.append((booking_id, acc_id, check_in_date.isoformat(), check_out_date.isoformat(), cost))

def generate_booking_transportations():
    if not bookings or not (flights or car_rentals or cruises):
        print("Error: Need bookings and transport options.")
        return
    booking_ids = list(range(1, len(bookings) + 1))
    flight_ids = list(range(1, len(flights) + 1))
    car_ids = list(range(1, len(car_rentals) + 1))
    cruise_ids = list(range(1, len(cruises) + 1))

    for booking_id in booking_ids:
        if random.random() < AVG_TRANSPORTS_PER_BOOKING:
            num_trans = random.randint(1, 3)
            for _ in range(num_trans):
                transport_type = random.choice([1, 2, 4]) # 1:Flight, 2:Car, 4:Cruise (No Bus link table)
                flight_id, car_id, cruise_id = None, None, None
                cost = 0

                if transport_type == 1 and flight_ids:
                    flight_id = random.choice(flight_ids)
                    cost = round(random.uniform(100, 2000), 2) # Estimate
                elif transport_type == 2 and car_ids:
                    car_id = random.choice(car_ids)
                    cost = round(random.uniform(100, 1000), 2) # Estimate
                elif transport_type == 4 and cruise_ids:
                    cruise_id = random.choice(cruise_ids)
                    cost = round(random.uniform(500, 5000), 2) # Estimate
                else:
                    continue # Skip if no transport of this type available

                booking_transportations.append((booking_id, transport_type, flight_id, car_id, cruise_id, cost))

def generate_payments():
    if not bookings:
        print("Error: Need bookings to generate payments.")
        return
    booking_ids = list(range(1, len(bookings) + 1))
    for booking_id in booking_ids:
         if random.random() < AVG_PAYMENTS_PER_BOOKING:
            payment_date = fake.date_between(start_date="-1y", end_date="today").isoformat()
            # Find booking cost approx
            booking_cost = next((b[4] for b in bookings if b == bookings[booking_id-1]), 1000) # Default if not found
            amount = round(booking_cost * random.uniform(0.8, 1.1), 2) # Payment amount around booking cost
            payment_type = random.choice(["Credit Card", "Debit Card", "Bank Transfer", "PayPal"])
            card_number = fake.credit_card_number() if "Card" in payment_type else None
            expiry_date = fake.credit_card_expire() if card_number else None
            # Store only last 4 digits for safety
            safe_card_number = f"**** **** **** {card_number[-4:]}" if card_number else None
            payments.append((booking_id, payment_date, amount, payment_type, safe_card_number, expiry_date))

def generate_reviews():
    if not booking_passengers:
        print("Error: Need booking_passengers link data.")
        return
    for booking_id, passenger_id in booking_passengers:
        if random.random() < AVG_REVIEWS_PER_BOOKING:
            rating = random.randint(1, 5)
            text = fake.paragraph(nb_sentences=random.randint(2, 5))
            review_date = fake.date_between(start_date="-6m", end_date="today").isoformat()
            reviews.append((booking_id, passenger_id, rating, text, review_date))

# --- Generate Data ---
print("Generating data...")
generate_locations(NUM_LOCATIONS)
generate_passengers(NUM_PASSENGERS)
generate_employees(NUM_EMPLOYEES)
# Assign supervisors (simple hierarchy: managers supervise agents/support)
manager_ids = [i + 1 for i, emp in enumerate(employees) if emp[1] == "Manager"]
non_manager_ids = [i + 1 for i, emp in enumerate(employees) if emp[1] != "Manager"]
if manager_ids:
    for i in range(len(employees)):
        if employees[i][1] != "Manager": # Assign supervisor only to non-managers
            supervisor_id = random.choice(manager_ids)
            # Create a new tuple with the supervisor ID
            employees[i] = employees[i][:3] + (supervisor_id,)

generate_accommodations(NUM_ACCOMMODATIONS)
generate_flights(NUM_FLIGHTS)
generate_car_rentals(NUM_CAR_RENTALS)
generate_cruises(NUM_CRUISES)
generate_bookings(NUM_BOOKINGS)
generate_booking_passengers()
generate_booking_accommodations()
generate_booking_transportations()
generate_payments()
generate_reviews()
print("Data generation complete.")

# --- Write to SQL File ---
print(f"Writing SQL INSERT statements to {output_sql_path}...")
with open(output_sql_path, "w", encoding="utf-8") as f:
    f.write("-- Travel Agency Data Population Script (SQLite)\n")
    f.write("PRAGMA foreign_keys = OFF; -- Disable FKs during bulk insert\n\n")

    # Helper to write inserts
    def write_inserts(table_name, columns, data):
        if not data: return
        f.write(f"-- Data for {table_name}\n")
        cols_str = ", ".join(columns)
        for row in data:
            # Prepare values with proper escaping for SQLite
            sql_literals = []
            for v in row:
                if v is None:
                    sql_literals.append("NULL")
                else:
                    # Convert to string and escape single quotes by doubling them
                    escaped_v = str(v).replace("'", "''")
                    sql_literals.append(f"'{escaped_v}'")
            values_str = ", ".join(sql_literals)
            f.write(f"INSERT INTO {table_name} ({cols_str}) VALUES ({values_str});\n")
        f.write("\n")

    write_inserts("Location", ["City", "State", "Country"], locations)
    write_inserts("Passenger", ["Name", "Gender", "Age", "Email", "Phone"], passengers)
    write_inserts("Employee", ["Name", "Role", "JoinDate", "SupervisorID"], employees)
    write_inserts("Accommodation", ["Name", "Type", "Rate", "Facilities", "Discount", "LocationID"], accommodations)
    # TransportationType already inserted in schema
    write_inserts("Flight", ["FlightNumber", "Carrier", "SourceLocationID", "DestLocationID", "DepartureDateTime", "ArrivalDateTime", "Class", "Fare"], flights)
    write_inserts("CarRental", ["Company", "CarType", "PickupLocationID", "DropoffLocationID", "PickupDateTime", "DropoffDateTime", "Rent"], car_rentals)
    write_inserts("Cruise", ["CruiseName", "Line", "SourceLocationID", "DestLocationID", "DepartureDate", "ReturnDate", "Fare"], cruises)
    write_inserts("Booking", ["GroupName", "Purpose", "BookingDate", "EmployeeID", "TotalCost"], bookings)
    write_inserts("BookingPassenger", ["BookingID", "PassengerID"], booking_passengers)
    write_inserts("BookingAccommodation", ["BookingID", "AccommodationID", "CheckInDate", "CheckOutDate", "Cost"], booking_accommodations)
    write_inserts("BookingTransportation", ["BookingID", "TransportTypeID", "FlightID", "CarRentalID", "CruiseID", "Cost"], booking_transportations)
    write_inserts("Payment", ["BookingID", "PaymentDate", "Amount", "PaymentType", "CardNumber", "ExpiryDate"], payments)
    write_inserts("Review", ["BookingID", "PassengerID", "Rating", "Text", "ReviewDate"], reviews)

    f.write("PRAGMA foreign_keys = ON; -- Re-enable FKs\n")

print("SQL file generated successfully.")

# --- Optional: Insert directly into DB for verification ---
# print(f"Inserting data into {db_path}...")
# try:
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute("PRAGMA foreign_keys = OFF;")
#     with open(output_sql_path, "r", encoding="utf-8") as f:
#         sql_script = f.read()
#     cursor.executescript(sql_script) # Execute the generated script
#     conn.commit()
#     print("Data inserted into database successfully.")
# except sqlite3.Error as e:
#     print(f"SQLite Error during insertion: {e}")
# finally:
#     if conn:
#         conn.close()

