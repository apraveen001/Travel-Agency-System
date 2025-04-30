import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='12345678',
                database='travelagency'
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                return True
        except Error as err:
            print(f"Error: {err}")
            return False

    def disconnect(self):
        if hasattr(self, 'connection') and self.connection and self.connection.is_connected():
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            self.connection.close()
            
    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Error as err:
            print(f"Error executing query: {err}")
            return False
            
    def fetch_all(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as err:
            print(f"Error fetching data: {err}")
            return []
            
    def fetch_one(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Error as err:
            print(f"Error fetching data: {err}")
            return None
            
    def get_last_insert_id(self):
        return self.cursor.lastrowid
