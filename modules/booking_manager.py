class BookingManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_bookings(self):
        query = """
        SELECT b.*, p.Name as PassengerName, e.Name as EmployeeName
        FROM Booking b
        JOIN Passenger p ON b.PassengerID = p.PassengerID
        LEFT JOIN AdminEmployee e ON b.EmployeeID = e.EmployeeID
        ORDER BY b.BookingDate DESC
        """
        return self.db.fetch_all(query)
    
    def get_booking_by_id(self, booking_id):
        query = """
        SELECT b.*, p.Name as PassengerName, e.Name as EmployeeName
        FROM Booking b
        JOIN Passenger p ON b.PassengerID = p.PassengerID
        LEFT JOIN AdminEmployee e ON b.EmployeeID = e.EmployeeID
        WHERE b.BookingID = %s
        """
        return self.db.fetch_one(query, (booking_id,))
    
    def add_booking(self, data):
        query = """INSERT INTO Booking 
                (PassengerID, BookingDate, TotalAmount, Status, EmployeeID)
                VALUES (%(passenger_id)s, %(booking_date)s, %(total_amount)s, %(status)s, %(employee_id)s)"""
        
        # Handle null employee
        if not data.get('employee_id'):
            data['employee_id'] = None
            
        # Set default booking date if not provided
        if not data.get('booking_date'):
            data['booking_date'] = None  # Will use DEFAULT CURRENT_TIMESTAMP
            
        success = self.db.execute_query(query, data)
        if success:
            return self.db.get_last_insert_id()
        return None
    
    def update_booking(self, booking_id, data):
        query = """UPDATE Booking SET
                PassengerID = %(passenger_id)s,
                TotalAmount = %(total_amount)s,
                Status = %(status)s,
                EmployeeID = %(employee_id)s
                WHERE BookingID = %(id)s"""
                
        # Handle null employee
        if not data.get('employee_id'):
            data['employee_id'] = None
            
        data['id'] = booking_id
        return self.db.execute_query(query, data)
    
    def delete_booking(self, booking_id):
        # Check for dependencies before deleting
        dependencies = [
            "BookingFlight",
            "BookingAccommodation",
            "BookingActivity",
            "BookingCarRental",
            "Payment",
            "Review"
        ]
        
        for table in dependencies:
            query = f"SELECT COUNT(*) as count FROM {table} WHERE BookingID = %s"
            result = self.db.fetch_one(query, (booking_id,))
            if result and result['count'] > 0:
                return False
        
        query = "DELETE FROM Booking WHERE BookingID = %s"
        return self.db.execute_query(query, (booking_id,))
    
    def search_bookings(self, search_term):
        query = """
        SELECT b.*, p.Name as PassengerName, e.Name as EmployeeName
        FROM Booking b
        JOIN Passenger p ON b.PassengerID = p.PassengerID
        LEFT JOIN AdminEmployee e ON b.EmployeeID = e.EmployeeID
        WHERE p.Name LIKE %s OR b.Status LIKE %s OR 
              CAST(b.BookingID AS CHAR) LIKE %s
        ORDER BY b.BookingDate DESC
        """
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern))
    
    # Methods for booking details (flights, accommodations, activities, car rentals)
    def get_booking_flights(self, booking_id):
        query = """
        SELECT bf.*, f.Carrier, f.Class, f.Fare,
               src.City as SourceCity, src.Country as SourceCountry,
               dst.City as DestinationCity, dst.Country as DestinationCountry,
               f.DepartureTime, f.ArrivalTime
        FROM BookingFlight bf
        JOIN Flight f ON bf.FlightNumber = f.FlightNumber
        JOIN Location src ON f.SourceID = src.LocationID
        JOIN Location dst ON f.DestinationID = dst.LocationID
        WHERE bf.BookingID = %s
        """
        return self.db.fetch_all(query, (booking_id,))
    
    def add_booking_flight(self, data):
        query = """INSERT INTO BookingFlight 
                (BookingID, FlightNumber, Passengers)
                VALUES (%(booking_id)s, %(flight_number)s, %(passengers)s)"""
        
        # Set default passengers if not provided
        if not data.get('passengers'):
            data['passengers'] = 1
            
        return self.db.execute_query(query, data)
    
    def update_booking_flight(self, booking_id, flight_number, passengers):
        query = """UPDATE BookingFlight SET
                Passengers = %s
                WHERE BookingID = %s AND FlightNumber = %s"""
        return self.db.execute_query(query, (passengers, booking_id, flight_number))
    
    def delete_booking_flight(self, booking_id, flight_number):
        query = "DELETE FROM BookingFlight WHERE BookingID = %s AND FlightNumber = %s"
        return self.db.execute_query(query, (booking_id, flight_number))
    
    def get_booking_accommodations(self, booking_id):
        query = """
        SELECT ba.*, a.Name, a.Type, a.Rate, a.Discount,
               l.City, l.Country
        FROM BookingAccommodation ba
        JOIN Accommodation a ON ba.AccommodationID = a.AccommodationID
        JOIN Location l ON a.LocationID = l.LocationID
        WHERE ba.BookingID = %s
        """
        return self.db.fetch_all(query, (booking_id,))
    
    def add_booking_accommodation(self, data):
        query = """INSERT INTO BookingAccommodation 
                (BookingID, AccommodationID, CheckInDate, CheckOutDate, Guests)
                VALUES (%(booking_id)s, %(accommodation_id)s, %(check_in_date)s, 
                        %(check_out_date)s, %(guests)s)"""
        
        # Set default guests if not provided
        if not data.get('guests'):
            data['guests'] = 1
            
        return self.db.execute_query(query, data)
    
    def update_booking_accommodation(self, booking_id, accommodation_id, data):
        query = """UPDATE BookingAccommodation SET
                CheckInDate = %(check_in_date)s,
                CheckOutDate = %(check_out_date)s,
                Guests = %(guests)s
                WHERE BookingID = %(booking_id)s AND AccommodationID = %(accommodation_id)s"""
        data['booking_id'] = booking_id
        data['accommodation_id'] = accommodation_id
        return self.db.execute_query(query, data)
    
    def delete_booking_accommodation(self, booking_id, accommodation_id):
        query = "DELETE FROM BookingAccommodation WHERE BookingID = %s AND AccommodationID = %s"
        return self.db.execute_query(query, (booking_id, accommodation_id))
    
    def get_booking_activities(self, booking_id):
        query = """
        SELECT ba.*, a.Name, a.Type, a.Cost,
               l.City, l.Country
        FROM BookingActivity ba
        JOIN Activity a ON ba.ActivityID = a.ActivityID
        JOIN Location l ON a.LocationID = l.LocationID
        WHERE ba.BookingID = %s
        """
        return self.db.fetch_all(query, (booking_id,))
    
    def add_booking_activity(self, data):
        query = """INSERT INTO BookingActivity 
                (BookingID, ActivityID, Participants, ScheduleDate)
                VALUES (%(booking_id)s, %(activity_id)s, %(participants)s, %(schedule_date)s)"""
        
        # Set default participants if not provided
        if not data.get('participants'):
            data['participants'] = 1
            
        return self.db.execute_query(query, data)
    
    def update_booking_activity(self, booking_id, activity_id, data):
        query = """UPDATE BookingActivity SET
                Participants = %(participants)s,
                ScheduleDate = %(schedule_date)s
                WHERE BookingID = %(booking_id)s AND ActivityID = %(activity_id)s"""
        data['booking_id'] = booking_id
        data['activity_id'] = activity_id
        return self.db.execute_query(query, data)
    
    def delete_booking_activity(self, booking_id, activity_id):
        query = "DELETE FROM BookingActivity WHERE BookingID = %s AND ActivityID = %s"
        return self.db.execute_query(query, (booking_id, activity_id))
    
    def get_booking_car_rentals(self, booking_id):
        query = """
        SELECT bcr.*, cr.CarType, cr.DailyRate,
               pickup.City as PickupCity, pickup.Country as PickupCountry,
               dropoff.City as DropoffCity, dropoff.Country as DropoffCountry
        FROM BookingCarRental bcr
        JOIN CarRental cr ON bcr.RentalID = cr.RentalID
        JOIN Location pickup ON cr.PickupLocationID = pickup.LocationID
        JOIN Location dropoff ON cr.DropoffLocationID = dropoff.LocationID
        WHERE bcr.BookingID = %s
        """
        return self.db.fetch_all(query, (booking_id,))
    
    def add_booking_car_rental(self, data):
        query = """INSERT INTO BookingCarRental 
                (BookingID, RentalID, StartDate, EndDate)
                VALUES (%(booking_id)s, %(rental_id)s, %(start_date)s, %(end_date)s)"""
        return self.db.execute_query(query, data)
    
    def update_booking_car_rental(self, booking_id, rental_id, data):
        query = """UPDATE BookingCarRental SET
                StartDate = %(start_date)s,
                EndDate = %(end_date)s
                WHERE BookingID = %(booking_id)s AND RentalID = %(rental_id)s"""
        data['booking_id'] = booking_id
        data['rental_id'] = rental_id
        return self.db.execute_query(query, data)
    
    def delete_booking_car_rental(self, booking_id, rental_id):
        query = "DELETE FROM BookingCarRental WHERE BookingID = %s AND RentalID = %s"
        return self.db.execute_query(query, (booking_id, rental_id))
