class FlightManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_flights(self):
        query = """
        SELECT f.*, 
               src.City as SourceCity, src.Country as SourceCountry,
               dst.City as DestinationCity, dst.Country as DestinationCountry
        FROM Flight f
        JOIN Location src ON f.SourceID = src.LocationID
        JOIN Location dst ON f.DestinationID = dst.LocationID
        ORDER BY f.DepartureTime
        """
        return self.db.fetch_all(query)
    
    def get_flight_by_number(self, flight_number):
        query = """
        SELECT f.*, 
               src.City as SourceCity, src.Country as SourceCountry,
               dst.City as DestinationCity, dst.Country as DestinationCountry
        FROM Flight f
        JOIN Location src ON f.SourceID = src.LocationID
        JOIN Location dst ON f.DestinationID = dst.LocationID
        WHERE f.FlightNumber = %s
        """
        return self.db.fetch_one(query, (flight_number,))
    
    def add_flight(self, data):
        query = """INSERT INTO Flight 
                (FlightNumber, Carrier, SourceID, DestinationID, Class, Fare, DepartureTime, ArrivalTime)
                VALUES (%(flight_number)s, %(carrier)s, %(source_id)s, %(destination_id)s, 
                        %(class)s, %(fare)s, %(departure_time)s, %(arrival_time)s)"""
        return self.db.execute_query(query, data)
    
    def update_flight(self, flight_number, data):
        query = """UPDATE Flight SET
                Carrier = %(carrier)s,
                SourceID = %(source_id)s,
                DestinationID = %(destination_id)s,
                Class = %(class)s,
                Fare = %(fare)s,
                DepartureTime = %(departure_time)s,
                ArrivalTime = %(arrival_time)s
                WHERE FlightNumber = %(flight_number)s"""
        data['flight_number'] = flight_number
        return self.db.execute_query(query, data)
    
    def delete_flight(self, flight_number):
        # Check for dependencies before deleting
        query = "SELECT COUNT(*) as count FROM BookingFlight WHERE FlightNumber = %s"
        result = self.db.fetch_one(query, (flight_number,))
        if result and result['count'] > 0:
            return False
        
        query = "DELETE FROM Flight WHERE FlightNumber = %s"
        return self.db.execute_query(query, (flight_number,))
    
    def search_flights(self, search_term):
        query = """
        SELECT f.*, 
               src.City as SourceCity, src.Country as SourceCountry,
               dst.City as DestinationCity, dst.Country as DestinationCountry
        FROM Flight f
        JOIN Location src ON f.SourceID = src.LocationID
        JOIN Location dst ON f.DestinationID = dst.LocationID
        WHERE f.FlightNumber LIKE %s OR f.Carrier LIKE %s OR 
              src.City LIKE %s OR dst.City LIKE %s
        ORDER BY f.DepartureTime
        """
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern, search_pattern))
