class LocationManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_locations(self):
        query = "SELECT * FROM Location ORDER BY Country, City"
        return self.db.fetch_all(query)
    
    def get_location_by_id(self, location_id):
        query = "SELECT * FROM Location WHERE LocationID = %s"
        return self.db.fetch_one(query, (location_id,))
    
    def add_location(self, data):
        query = """INSERT INTO Location 
                (City, State, Country)
                VALUES (%(city)s, %(state)s, %(country)s)"""
        return self.db.execute_query(query, data)
    
    def update_location(self, location_id, data):
        query = """UPDATE Location SET
                City = %(city)s,
                State = %(state)s,
                Country = %(country)s
                WHERE LocationID = %(id)s"""
        data['id'] = location_id
        return self.db.execute_query(query, data)
    
    def delete_location(self, location_id):
        # Check for dependencies before deleting
        dependencies = [
            ("Accommodation", "LocationID"),
            ("Flight", "SourceID"),
            ("Flight", "DestinationID"),
            ("Cruise", "SourceID"),
            ("Cruise", "DestinationID"),
            ("CarRental", "PickupLocationID"),
            ("CarRental", "DropoffLocationID"),
            ("Activity", "LocationID")
        ]
        
        for table, column in dependencies:
            query = f"SELECT COUNT(*) as count FROM {table} WHERE {column} = %s"
            result = self.db.fetch_one(query, (location_id,))
            if result and result['count'] > 0:
                return False
        
        query = "DELETE FROM Location WHERE LocationID = %s"
        return self.db.execute_query(query, (location_id,))
    
    def search_locations(self, search_term):
        query = """SELECT * FROM Location 
                WHERE City LIKE %s OR Country LIKE %s 
                ORDER BY Country, City"""
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern))
