class CruiseManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_cruises(self):
        query = """
        SELECT c.*, 
               src.City as SourceCity, src.Country as SourceCountry,
               dst.City as DestinationCity, dst.Country as DestinationCountry
        FROM Cruise c
        JOIN Location src ON c.SourceID = src.LocationID
        JOIN Location dst ON c.DestinationID = dst.LocationID
        ORDER BY c.DepartureDate
        """
        return self.db.fetch_all(query)
    
    def get_cruise_by_id(self, cruise_id):
        query = """
        SELECT c.*, 
               src.City as SourceCity, src.Country as SourceCountry,
               dst.City as DestinationCity, dst.Country as DestinationCountry
        FROM Cruise c
        JOIN Location src ON c.SourceID = src.LocationID
        JOIN Location dst ON c.DestinationID = dst.LocationID
        WHERE c.CruiseID = %s
        """
        return self.db.fetch_one(query, (cruise_id,))
    
    def add_cruise(self, data):
        query = """INSERT INTO Cruise 
                (Name, SourceID, DestinationID, Fare, DepartureDate, ReturnDate)
                VALUES (%(name)s, %(source_id)s, %(destination_id)s, 
                        %(fare)s, %(departure_date)s, %(return_date)s)"""
        return self.db.execute_query(query, data)
    
    def update_cruise(self, cruise_id, data):
        query = """UPDATE Cruise SET
                Name = %(name)s,
                SourceID = %(source_id)s,
                DestinationID = %(destination_id)s,
                Fare = %(fare)s,
                DepartureDate = %(departure_date)s,
                ReturnDate = %(return_date)s
                WHERE CruiseID = %(id)s"""
        data['id'] = cruise_id
        return self.db.execute_query(query, data)
    
    def delete_cruise(self, cruise_id):
        # In a real application, we would check for bookings related to this cruise
        # For now, we'll just delete the cruise
        query = "DELETE FROM Cruise WHERE CruiseID = %s"
        return self.db.execute_query(query, (cruise_id,))
    
    def search_cruises(self, search_term):
        query = """
        SELECT c.*, 
               src.City as SourceCity, src.Country as SourceCountry,
               dst.City as DestinationCity, dst.Country as DestinationCountry
        FROM Cruise c
        JOIN Location src ON c.SourceID = src.LocationID
        JOIN Location dst ON c.DestinationID = dst.LocationID
        WHERE c.Name LIKE %s OR 
              src.City LIKE %s OR dst.City LIKE %s OR
              src.Country LIKE %s OR dst.Country LIKE %s
        ORDER BY c.DepartureDate
        """
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
