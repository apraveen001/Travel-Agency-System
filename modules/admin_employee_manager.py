class AdminEmployeeManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_employees(self):
        query = """
        SELECT e.*, s.Name as SupervisorName 
        FROM AdminEmployee e
        LEFT JOIN AdminEmployee s ON e.SupervisorID = s.EmployeeID
        ORDER BY e.Name
        """
        return self.db.fetch_all(query)
    
    def get_employee_by_id(self, employee_id):
        query = """
        SELECT e.*, s.Name as SupervisorName 
        FROM AdminEmployee e
        LEFT JOIN AdminEmployee s ON e.SupervisorID = s.EmployeeID
        WHERE e.EmployeeID = %s
        """
        return self.db.fetch_one(query, (employee_id,))
    
    def get_supervisors(self):
        query = "SELECT EmployeeID, Name FROM AdminEmployee ORDER BY Name"
        return self.db.fetch_all(query)
    
    def add_employee(self, data):
        query = """INSERT INTO AdminEmployee 
                (Name, Role, JoinDate, SupervisorID)
                VALUES (%(name)s, %(role)s, %(join_date)s, %(supervisor_id)s)"""
        
        # Handle null supervisor
        if not data.get('supervisor_id'):
            data['supervisor_id'] = None
            
        return self.db.execute_query(query, data)
    
    def update_employee(self, employee_id, data):
        query = """UPDATE AdminEmployee SET
                Name = %(name)s,
                Role = %(role)s,
                JoinDate = %(join_date)s,
                SupervisorID = %(supervisor_id)s
                WHERE EmployeeID = %(id)s"""
                
        # Handle null supervisor
        if not data.get('supervisor_id'):
            data['supervisor_id'] = None
            
        data['id'] = employee_id
        return self.db.execute_query(query, data)
    
    def delete_employee(self, employee_id):
        # Check for dependencies before deleting
        dependencies = [
            ("AdminEmployee", "SupervisorID"),
            ("Booking", "EmployeeID")
        ]
        
        for table, column in dependencies:
            query = f"SELECT COUNT(*) as count FROM {table} WHERE {column} = %s"
            result = self.db.fetch_one(query, (employee_id,))
            if result and result['count'] > 0:
                return False
        
        query = "DELETE FROM AdminEmployee WHERE EmployeeID = %s"
        return self.db.execute_query(query, (employee_id,))
    
    def search_employees(self, search_term):
        query = """
        SELECT e.*, s.Name as SupervisorName 
        FROM AdminEmployee e
        LEFT JOIN AdminEmployee s ON e.SupervisorID = s.EmployeeID
        WHERE e.Name LIKE %s OR e.Role LIKE %s 
        ORDER BY e.Name
        """
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern))
