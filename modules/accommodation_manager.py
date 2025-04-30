class AccommodationManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_accommodations(self):
        query = """
        SELECT a.*, l.City, l.Country 
        FROM Accommodation a
        JOIN Location l ON a.LocationID = l.LocationID
        ORDER BY a.Name
        """
        return self.db.fetch_all(query)
    
    def get_accommodation_by_id(self, accommodation_id):
        query = """
        SELECT a.*, l.City, l.Country 
        FROM Accommodation a
        JOIN Location l ON a.LocationID = l.LocationID
        WHERE a.AccommodationID = %s
        """
        return self.db.fetch_one(query, (accommodation_id,))
    
    def add_accommodation(self, data):
        query = """INSERT INTO Accommodation 
                (Name, Type, Rate, LocationID, Facilities, Discount)
                VALUES (%(name)s, %(type)s, %(rate)s, %(location_id)s, %(facilities)s, %(discount)s)"""
        
        # Handle default discount
        if 'discount' not in data or data['discount'] is None:
            data['discount'] = 0.00
            
        return self.db.execute_query(query, data)
    
    def update_accommodation(self, accommodation_id, data):
        query = """UPDATE Accommodation SET
                Name = %(name)s,
                Type = %(type)s,
                Rate = %(rate)s,
                LocationID = %(location_id)s,
                Facilities = %(facilities)s,
                Discount = %(discount)s
                WHERE AccommodationID = %(id)s"""
                
        # Handle default discount
        if 'discount' not in data or data['discount'] is None:
            data['discount'] = 0.00
            
        data['id'] = accommodation_id
        return self.db.execute_query(query, data)
    
    def delete_accommodation(self, accommodation_id):
        # Check for dependencies before deleting
        query = "SELECT COUNT(*) as count FROM BookingAccommodation WHERE AccommodationID = %s"
        result = self.db.fetch_one(query, (accommodation_id,))
        if result and result['count'] > 0:
            return False
        
        query = "DELETE FROM Accommodation WHERE AccommodationID = %s"
        return self.db.execute_query(query, (accommodation_id,))
    
    def search_accommodations(self, search_term):
        query = """
        SELECT a.*, l.City, l.Country 
        FROM Accommodation a
        JOIN Location l ON a.LocationID = l.LocationID
        WHERE a.Name LIKE %s OR l.City LIKE %s OR l.Country LIKE %s
        ORDER BY a.Name
        """
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern))
