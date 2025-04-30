class ActivityManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_activities(self):
        query = """
        SELECT a.*, l.City, l.Country 
        FROM Activity a
        JOIN Location l ON a.LocationID = l.LocationID
        ORDER BY a.Name
        """
        return self.db.fetch_all(query)
    
    def get_activity_by_id(self, activity_id):
        query = """
        SELECT a.*, l.City, l.Country 
        FROM Activity a
        JOIN Location l ON a.LocationID = l.LocationID
        WHERE a.ActivityID = %s
        """
        return self.db.fetch_one(query, (activity_id,))
    
    def add_activity(self, data):
        query = """INSERT INTO Activity 
                (Name, Type, LocationID, Cost, Description)
                VALUES (%(name)s, %(type)s, %(location_id)s, %(cost)s, %(description)s)"""
        return self.db.execute_query(query, data)
    
    def update_activity(self, activity_id, data):
        query = """UPDATE Activity SET
                Name = %(name)s,
                Type = %(type)s,
                LocationID = %(location_id)s,
                Cost = %(cost)s,
                Description = %(description)s
                WHERE ActivityID = %(id)s"""
        data['id'] = activity_id
        return self.db.execute_query(query, data)
    
    def delete_activity(self, activity_id):
        # Check for dependencies before deleting
        query = "SELECT COUNT(*) as count FROM BookingActivity WHERE ActivityID = %s"
        result = self.db.fetch_one(query, (activity_id,))
        if result and result['count'] > 0:
            return False
        
        query = "DELETE FROM Activity WHERE ActivityID = %s"
        return self.db.execute_query(query, (activity_id,))
    
    def search_activities(self, search_term):
        query = """
        SELECT a.*, l.City, l.Country 
        FROM Activity a
        JOIN Location l ON a.LocationID = l.LocationID
        WHERE a.Name LIKE %s OR a.Type LIKE %s OR 
              l.City LIKE %s OR l.Country LIKE %s OR
              a.Description LIKE %s
        ORDER BY a.Name
        """
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
