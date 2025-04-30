class PassengerManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_passengers(self):
        query = "SELECT * FROM Passenger ORDER BY Name"
        return self.db.fetch_all(query)
    
    def get_passenger_by_id(self, passenger_id):
        query = "SELECT * FROM Passenger WHERE PassengerID = %s"
        return self.db.fetch_one(query, (passenger_id,))
    
    def add_passenger(self, data):
        query = """INSERT INTO Passenger 
                (Name, Gender, Age, Email, Phone)
                VALUES (%(name)s, %(gender)s, %(age)s, %(email)s, %(phone)s)"""
        return self.db.execute_query(query, data)
    
    def update_passenger(self, passenger_id, data):
        query = """UPDATE Passenger SET
                Name = %(name)s,
                Gender = %(gender)s,
                Age = %(age)s,
                Email = %(email)s,
                Phone = %(phone)s
                WHERE PassengerID = %(id)s"""
        data['id'] = passenger_id
        return self.db.execute_query(query, data)
    
    def delete_passenger(self, passenger_id):
        # Check for dependencies before deleting
        dependencies = [
            ("Booking", "PassengerID"),
            ("TravelGroup", "CreatedBy"),
            ("GroupMember", "PassengerID")
        ]
        
        for table, column in dependencies:
            query = f"SELECT COUNT(*) as count FROM {table} WHERE {column} = %s"
            result = self.db.fetch_one(query, (passenger_id,))
            if result and result['count'] > 0:
                return False
        
        query = "DELETE FROM Passenger WHERE PassengerID = %s"
        return self.db.execute_query(query, (passenger_id,))
    
    def search_passengers(self, search_term):
        query = """SELECT * FROM Passenger 
                WHERE Name LIKE %s OR Email LIKE %s 
                ORDER BY Name"""
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern))
