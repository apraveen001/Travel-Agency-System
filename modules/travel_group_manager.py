class TravelGroupManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_travel_groups(self):
        query = """
        SELECT tg.*, p.Name as CreatorName
        FROM TravelGroup tg
        JOIN Passenger p ON tg.CreatedBy = p.PassengerID
        ORDER BY tg.CreatedDate DESC
        """
        return self.db.fetch_all(query)
    
    def get_travel_group_by_id(self, group_id):
        query = """
        SELECT tg.*, p.Name as CreatorName
        FROM TravelGroup tg
        JOIN Passenger p ON tg.CreatedBy = p.PassengerID
        WHERE tg.GroupID = %s
        """
        return self.db.fetch_one(query, (group_id,))
    
    def add_travel_group(self, data):
        query = """INSERT INTO TravelGroup 
                (GroupName, Purpose, CreatedBy, CreatedDate)
                VALUES (%(group_name)s, %(purpose)s, %(created_by)s, %(created_date)s)"""
        
        # Set default created date if not provided
        if not data.get('created_date'):
            data['created_date'] = None  # Will use DEFAULT CURRENT_DATE
            
        success = self.db.execute_query(query, data)
        if success:
            return self.db.get_last_insert_id()
        return None
    
    def update_travel_group(self, group_id, data):
        query = """UPDATE TravelGroup SET
                GroupName = %(group_name)s,
                Purpose = %(purpose)s
                WHERE GroupID = %(id)s"""
        data['id'] = group_id
        return self.db.execute_query(query, data)
    
    def delete_travel_group(self, group_id):
        # First delete all group members
        member_query = "DELETE FROM GroupMember WHERE GroupID = %s"
        self.db.execute_query(member_query, (group_id,))
        
        # Then delete the group
        query = "DELETE FROM TravelGroup WHERE GroupID = %s"
        return self.db.execute_query(query, (group_id,))
    
    def search_travel_groups(self, search_term):
        query = """
        SELECT tg.*, p.Name as CreatorName
        FROM TravelGroup tg
        JOIN Passenger p ON tg.CreatedBy = p.PassengerID
        WHERE tg.GroupName LIKE %s OR tg.Purpose LIKE %s OR p.Name LIKE %s
        ORDER BY tg.CreatedDate DESC
        """
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern))
    
    # Group member management
    def get_group_members(self, group_id):
        query = """
        SELECT gm.*, p.Name, p.Email, p.Phone
        FROM GroupMember gm
        JOIN Passenger p ON gm.PassengerID = p.PassengerID
        WHERE gm.GroupID = %s
        ORDER BY gm.JoinDate
        """
        return self.db.fetch_all(query, (group_id,))
    
    def add_group_member(self, data):
        query = """INSERT INTO GroupMember 
                (GroupID, PassengerID, JoinDate)
                VALUES (%(group_id)s, %(passenger_id)s, %(join_date)s)"""
        
        # Set default join date if not provided
        if not data.get('join_date'):
            data['join_date'] = None  # Will use DEFAULT CURRENT_DATE
            
        return self.db.execute_query(query, data)
    
    def delete_group_member(self, group_id, passenger_id):
        query = "DELETE FROM GroupMember WHERE GroupID = %s AND PassengerID = %s"
        return self.db.execute_query(query, (group_id, passenger_id))
