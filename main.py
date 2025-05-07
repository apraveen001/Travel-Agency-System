# -*- coding: utf-8 -*-
import sys
import os
from collections import defaultdict

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from src.database import db, init_app, MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, DATABASE_NAME
from sqlalchemy.sql import text
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.urandom(24)

# Initialize database
try:
    init_app(app)
except SystemExit as e:
    print(f"Failed to initialize database connection: {e}")
    sys.exit(1)

# --- SQLAlchemy Models (Keep for reference/potential future use, but direct SQL used for transactions) ---
class Location(db.Model):
    __tablename__ = "Location"
    LocationID = db.Column(db.Integer, primary_key=True)
    City = db.Column(db.String(100), nullable=False)
    State = db.Column(db.String(100))
    Country = db.Column(db.String(100), nullable=False)

class Passenger(db.Model):
    __tablename__ = "Passenger"
    PassengerID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    Gender = db.Column(db.String(10))
    Age = db.Column(db.Integer)
    Email = db.Column(db.String(255), unique=True)
    Phone = db.Column(db.String(20))

# --- Helper Functions ---
def get_mysql_conn():
    """Establishes a direct connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=DATABASE_NAME,
            port=MYSQL_PORT
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        flash(f"Database connection error: {e}", "error")
        return None

def fetch_table_data(table_name, limit=100):
    """Helper to fetch data from a given table."""
    conn = None
    cursor = None
    rows = []
    columns = []
    try:
        conn = get_mysql_conn()
        if conn is None: return [], []
        
        cursor = conn.cursor(dictionary=True)
        # Use backticks for table names to handle potential reserved keywords
        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT %s", (limit,))
        rows_dict = cursor.fetchall()
        if rows_dict:
            columns = list(rows_dict[0].keys())
            # Convert each row dictionary to a list of values in column order
            rows = [[row[col] for col in columns] for row in rows_dict]
    except Error as e:
        flash(f"Error fetching data from {table_name}: {e}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
    return rows, columns

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/schema")
def view_schema():
    try:
        schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                        "sql", "create_schema_mysql.sql")
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        return render_template("view_sql.html", title="Database Schema (MySQL)", sql_content=schema_sql)
    except FileNotFoundError:
        flash("MySQL Schema file not found.", "error")
        return redirect(url_for("index"))

@app.route("/populate")
def view_populate():
    try:
        populate_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          "sql", "populate_data_mysql.sql")
        with open(populate_path, "r") as f:
            populate_sql = f.read()
        return render_template("view_sql.html", title="Database Population Data (MySQL)", sql_content=populate_sql)
    except FileNotFoundError:
        flash("MySQL Population script not found.", "error")
        return redirect(url_for("index"))

@app.route("/queries")
def view_queries():
    try:
        queries_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                         "sql", "complex_queries.sql")
        with open(queries_path, "r") as f:
            queries_sql = f.read()
        return render_template("view_sql.html", title="Complex Queries", sql_content=queries_sql)
    except FileNotFoundError:
        flash("Complex queries file not found.", "error")
        return redirect(url_for("index"))

@app.route("/execute_sql", methods=["GET", "POST"])
def execute_sql():
    result = None
    error = None
    sql_command = ""
    columns = []

    if request.method == "POST":
        sql_command = request.form.get("sql_command", "").strip()
        action = request.form.get("action", "")
        
        if not sql_command:
            flash("No SQL command provided.", "warning")
            return render_template("execute_sql.html", 
                                 result=result, 
                                 error=error, 
                                 sql_command=sql_command, 
                                 columns=columns)

        conn = None
        cursor = None
        try:
            conn = get_mysql_conn()
            if conn is None:
                return render_template("execute_sql.html", 
                                     result=result, 
                                     error="Database connection failed", 
                                     sql_command=sql_command, 
                                     columns=columns)

            cursor = conn.cursor(dictionary=True)

            if action == "execute_script":
                flash("Multi-statement execution not supported via this interface.", "warning")
            elif action == "execute_query" and sql_command:
                # Basic check for potentially modifying commands
                is_select = sql_command.lower().strip().startswith("select") or sql_command.lower().strip().startswith("show") or sql_command.lower().strip().startswith("describe")
                
                cursor.execute(sql_command)
                
                if is_select and cursor.description:
                    result = cursor.fetchall()
                    if result:
                        columns = list(result[0].keys())
                        flash(f"Query executed successfully. Found {len(result)} rows.", "success")
                    else:
                        columns = [desc[0] for desc in cursor.description]
                        flash("Query executed, but returned no results.", "info")
                else:
                    conn.commit()
                    flash(f"Command executed successfully. Rows affected: {cursor.rowcount}", "success")
            else:
                flash("Invalid action or empty command.", "warning")

        except Error as e:
            error = f"MySQL Error: {e}"
            flash(error, "error")
            if conn:
                conn.rollback()
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    return render_template("execute_sql.html", 
                         result=result, 
                         error=error, 
                         sql_command=sql_command, 
                         columns=columns)

# --- Transaction Operations ---
@app.route("/add_passenger", methods=["GET", "POST"])
def add_passenger():
    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        age_str = request.form.get("age")
        email = request.form.get("email")
        phone = request.form.get("phone")

        # Basic Validation
        if not name:
            flash("Passenger name is required.", "error")
            return render_template("add_passenger.html", form_data=request.form)
        
        age = None
        if age_str:
            try:
                age = int(age_str)
                if not (0 < age < 120):
                    flash("Invalid age provided.", "error")
                    return render_template("add_passenger.html", form_data=request.form)
            except ValueError:
                flash("Age must be a number.", "error")
                return render_template("add_passenger.html", form_data=request.form)

        conn = None
        cursor = None
        try:
            conn = get_mysql_conn()
            if conn is None:
                # Flash message already set by get_mysql_conn
                return render_template("add_passenger.html", form_data=request.form)
            
            cursor = conn.cursor()
            sql = "INSERT INTO Passenger (Name, Gender, Age, Email, Phone) VALUES (%s, %s, %s, %s, %s)"
            # Handle potentially empty optional fields
            val = (name, gender if gender else None, age, email if email else None, phone if phone else None)
            cursor.execute(sql, val)
            conn.commit()
            flash(f"Passenger ", "success")
            return redirect(url_for("view_passengers"))

        except Error as e:
            # Check for unique constraint violation (e.g., duplicate email)
            if e.errno == 1062: # MySQL error code for duplicate entry
                 flash(f"Failed to add passenger: Email ", "error")
            else:
                flash(f"Failed to add passenger: {e}", "error")
            if conn:
                conn.rollback()
            return render_template("add_passenger.html", form_data=request.form)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    # GET request
    return render_template("add_passenger.html", form_data={})

@app.route("/available_options")
def available_options():
    """Lists available accommodations and flights."""
    accommodations_rows, accommodations_columns = fetch_table_data("Accommodation", limit=200) # Increase limit if needed
    flights_rows, flights_columns = fetch_table_data("Flight", limit=200) # Increase limit if needed
    
    return render_template("available_options.html", 
                           accommodations_rows=accommodations_rows, 
                           accommodations_columns=accommodations_columns,
                           flights_rows=flights_rows,
                           flights_columns=flights_columns)

@app.route("/passenger_itinerary/<int:passenger_id>")
def passenger_itinerary(passenger_id):
    """Displays the full itinerary for a given passenger."""
    conn = None
    cursor = None
    passenger = None
    bookings_data = defaultdict(lambda: {"details": None, "accommodations": [], "transportations": []})

    try:
        conn = get_mysql_conn()
        if conn is None:
            return redirect(url_for("view_passengers")) # Redirect if DB connection fails

        cursor = conn.cursor(dictionary=True)

        # 1. Fetch Passenger Details
        cursor.execute("SELECT * FROM Passenger WHERE PassengerID = %s", (passenger_id,))
        passenger = cursor.fetchone()
        if not passenger:
            flash(f"Passenger with ID {passenger_id} not found.", "error")
            return redirect(url_for("view_passengers"))

        # 2. Fetch Itinerary Details (Bookings, Accommodations, Transportations)
        # This complex query joins all relevant tables to get a flat list of itinerary components
        sql = """
        SELECT 
            b.BookingID, b.GroupName, b.Purpose, b.BookingDate, b.TotalCost, b.Status,
            e.Name AS AgentName,
            ba.BookingAccommodationID, ba.CheckInDate, ba.CheckOutDate, ba.Cost AS AccommodationCost,
            acc.Name AS AccommodationName, acc.Type AS AccommodationType,
            acc_loc.City AS AccommodationCity, acc_loc.Country AS AccommodationCountry,
            bt.BookingTransportationID, bt.Cost AS TransportCost,
            tt.Name AS TransportType,
            f.FlightID, f.FlightNumber, f.Carrier, f.DepartureDateTime AS FlightDeparture, f.ArrivalDateTime AS FlightArrival, f.Class AS FlightClass, f.Fare AS FlightFare,
            fl_src.City AS FlightSourceCity, fl_src.Country AS FlightSourceCountry,
            fl_dest.City AS FlightDestCity, fl_dest.Country AS FlightDestCountry,
            cr.CarRentalID, cr.Company AS CarCompany, cr.CarType, cr.PickupDateTime AS CarPickup, cr.DropoffDateTime AS CarDropoff, cr.Rent AS CarRent,
            cr_pick.City AS CarPickupCity, cr_pick.Country AS CarPickupCountry,
            cr_drop.City AS CarDropoffCity, cr_drop.Country AS CarDropoffCountry,
            cru.CruiseID, cru.CruiseName, cru.Line AS CruiseLine, cru.DepartureDate AS CruiseDeparture, cru.ReturnDate AS CruiseReturn, cru.Fare AS CruiseFare,
            cru_src.City AS CruiseSourceCity, cru_src.Country AS CruiseSourceCountry,
            cru_dest.City AS CruiseDestCity, cru_dest.Country AS CruiseDestCountry
        FROM Passenger p
        JOIN BookingPassenger bp ON p.PassengerID = bp.PassengerID
        JOIN Booking b ON bp.BookingID = b.BookingID
        LEFT JOIN Employee e ON b.EmployeeID = e.EmployeeID
        LEFT JOIN BookingAccommodation ba ON b.BookingID = ba.BookingID
        LEFT JOIN Accommodation acc ON ba.AccommodationID = acc.AccommodationID
        LEFT JOIN Location acc_loc ON acc.LocationID = acc_loc.LocationID
        LEFT JOIN BookingTransportation bt ON b.BookingID = bt.BookingID
        LEFT JOIN TransportationType tt ON bt.TransportTypeID = tt.TransportTypeID
        LEFT JOIN Flight f ON bt.FlightID = f.FlightID
        LEFT JOIN Location fl_src ON f.SourceLocationID = fl_src.LocationID
        LEFT JOIN Location fl_dest ON f.DestLocationID = fl_dest.LocationID
        LEFT JOIN CarRental cr ON bt.CarRentalID = cr.CarRentalID
        LEFT JOIN Location cr_pick ON cr.PickupLocationID = cr_pick.LocationID
        LEFT JOIN Location cr_drop ON cr.DropoffLocationID = cr_drop.LocationID
        LEFT JOIN Cruise cru ON bt.CruiseID = cru.CruiseID
        LEFT JOIN Location cru_src ON cru.SourceLocationID = cru_src.LocationID
        LEFT JOIN Location cru_dest ON cru.DestLocationID = cru_dest.LocationID
        WHERE p.PassengerID = %s
        ORDER BY b.BookingDate DESC, b.BookingID, ba.CheckInDate, bt.BookingTransportationID;
        """
        cursor.execute(sql, (passenger_id,))
        results = cursor.fetchall()

        # 3. Process and Structure the Results
        processed_acc_ids = set()
        processed_trans_ids = set()

        for row in results:
            booking_id = row["BookingID"]
            
            # Store booking details (only once per booking)
            if bookings_data[booking_id]["details"] is None:
                bookings_data[booking_id]["details"] = {
                    "BookingID": booking_id,
                    "GroupName": row["GroupName"],
                    "Purpose": row["Purpose"],
                    "BookingDate": row["BookingDate"],
                    "TotalCost": row["TotalCost"],
                    "Status": row["Status"],
                    "AgentName": row["AgentName"]
                }

            # Add accommodation details (avoid duplicates)
            acc_id = row["BookingAccommodationID"]
            if acc_id is not None and acc_id not in processed_acc_ids:
                bookings_data[booking_id]["accommodations"].append({
                    "Name": row["AccommodationName"],
                    "Type": row["AccommodationType"],
                    "City": row["AccommodationCity"],
                    "Country": row["AccommodationCountry"],
                    "CheckInDate": row["CheckInDate"],
                    "CheckOutDate": row["CheckOutDate"],
                    "Cost": row["AccommodationCost"]
                })
                processed_acc_ids.add(acc_id)

            # Add transportation details (avoid duplicates)
            trans_id = row["BookingTransportationID"]
            if trans_id is not None and trans_id not in processed_trans_ids:
                transport_details = {
                    "TransportType": row["TransportType"],
                    "Cost": row["TransportCost"]
                }
                if row["TransportType"] == "Flight" and row["FlightID"] is not None:
                    transport_details.update({
                        "FlightNumber": row["FlightNumber"],
                        "Carrier": row["Carrier"],
                        "SourceCity": row["FlightSourceCity"], "SourceCountry": row["FlightSourceCountry"],
                        "DestCity": row["FlightDestCity"], "DestCountry": row["FlightDestCountry"],
                        "DepartureDateTime": row["FlightDeparture"],
                        "ArrivalDateTime": row["FlightArrival"],
                        "Class": row["FlightClass"],
                        "Fare": row["FlightFare"]
                    })
                elif row["TransportType"] == "Car Rental" and row["CarRentalID"] is not None:
                     transport_details.update({
                        "Company": row["CarCompany"],
                        "CarType": row["CarType"],
                        "PickupCity": row["CarPickupCity"], "PickupCountry": row["CarPickupCountry"],
                        "DropoffCity": row["CarDropoffCity"], "DropoffCountry": row["CarDropoffCountry"],
                        "PickupDateTime": row["CarPickup"],
                        "DropoffDateTime": row["CarDropoff"],
                        "Rent": row["CarRent"]
                    })
                elif row["TransportType"] == "Cruise" and row["CruiseID"] is not None:
                     transport_details.update({
                        "CruiseName": row["CruiseName"],
                        "Line": row["CruiseLine"],
                        "SourceCity": row["CruiseSourceCity"], "SourceCountry": row["CruiseSourceCountry"],
                        "DestCity": row["CruiseDestCity"], "DestCountry": row["CruiseDestCountry"],
                        "DepartureDate": row["CruiseDeparture"],
                        "ReturnDate": row["CruiseReturn"],
                        "Fare": row["CruiseFare"]
                    })
                # Add other transport types if necessary
                
                bookings_data[booking_id]["transportations"].append(transport_details)
                processed_trans_ids.add(trans_id)

    except Error as e:
        flash(f"Error fetching itinerary: {e}", "error")
        # Optionally log the error
        print(f"Database error fetching itinerary for passenger {passenger_id}: {e}")
        return redirect(url_for("view_passengers"))
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

    # Convert defaultdict to a list of booking dictionaries for the template
    structured_bookings = [data["details"] | {"accommodations": data["accommodations"], "transportations": data["transportations"]} 
                           for data in bookings_data.values() if data["details"]]

    return render_template("passenger_itinerary.html", passenger=passenger, bookings=structured_bookings)


# --- Data Viewing Routes ---
@app.route("/locations")
def view_locations():
    rows, columns = fetch_table_data("Location")
    return render_template("view_table.html", title="Locations", rows=rows, columns=columns)

@app.route("/passengers")
def view_passengers():
    rows, columns = fetch_table_data("Passenger")
    # Pass table name and primary key column name for itinerary link generation
    return render_template("view_table.html", title="Passengers", rows=rows, columns=columns, table_name="Passenger", pk_column="PassengerID")

@app.route("/employees")
def view_employees():
    rows, columns = fetch_table_data("Employee")
    return render_template("view_table.html", title="Employees", rows=rows, columns=columns)

@app.route("/flights")
def view_flights():
    rows, columns = fetch_table_data("Flight")
    return render_template("view_table.html", title="Flights", rows=rows, columns=columns)

@app.route("/bookings")
def view_bookings():
    rows, columns = fetch_table_data("Booking")
    return render_template("view_table.html", title="Bookings", rows=rows, columns=columns)

# Add routes for other tables if needed (e.g., Accommodation, CarRental, Cruise)
@app.route("/accommodations")
def view_accommodations():
    rows, columns = fetch_table_data("Accommodation")
    return render_template("view_table.html", title="Accommodations", rows=rows, columns=columns)

@app.route("/car_rentals")
def view_car_rentals():
    rows, columns = fetch_table_data("CarRental")
    return render_template("view_table.html", title="Car Rentals", rows=rows, columns=columns)

@app.route("/cruises")
def view_cruises():
    rows, columns = fetch_table_data("Cruise")
    return render_template("view_table.html", title="Cruises", rows=rows, columns=columns)

if __name__ == "__main__":
    with app.app_context():
        inspector = db.inspect(db.engine)
        if not inspector.has_table("Location"):
            print("Database tables not found!")
            print("Please ensure the schema from 'sql/create_schema_mysql.sql' has been applied.")
            print("You might need to set environment variables for DB connection:")
            print("MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, DATABASE_NAME")
        else:
            print("Database tables exist. Starting application.")

    print(f"Flask app running on http://0.0.0.0:5000")
    print(f"Connect to MySQL DB: {DATABASE_NAME} on {MYSQL_HOST}:{MYSQL_PORT}")
    # Turn off debug mode for production/safer testing
    app.run(host="0.0.0.0", port=5000, debug=False)
