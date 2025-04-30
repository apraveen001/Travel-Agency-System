class PaymentManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_payments(self):
        query = """
        SELECT p.*, b.PassengerID, pas.Name as PassengerName
        FROM Payment p
        JOIN Booking b ON p.BookingID = b.BookingID
        JOIN Passenger pas ON b.PassengerID = pas.PassengerID
        ORDER BY p.PaymentDate DESC
        """
        return self.db.fetch_all(query)
    
    def get_payments_by_booking(self, booking_id):
        query = """
        SELECT p.*
        FROM Payment p
        WHERE p.BookingID = %s
        ORDER BY p.PaymentDate DESC
        """
        return self.db.fetch_all(query, (booking_id,))
    
    def get_payment_by_id(self, payment_id):
        query = """
        SELECT p.*, b.PassengerID, pas.Name as PassengerName
        FROM Payment p
        JOIN Booking b ON p.BookingID = b.BookingID
        JOIN Passenger pas ON b.PassengerID = pas.PassengerID
        WHERE p.PaymentID = %s
        """
        return self.db.fetch_one(query, (payment_id,))
    
    def add_payment(self, data):
        query = """INSERT INTO Payment 
                (BookingID, Amount, Method, TransactionID, PaymentDate, Status)
                VALUES (%(booking_id)s, %(amount)s, %(method)s, %(transaction_id)s, 
                        %(payment_date)s, %(status)s)"""
        
        # Set default payment date if not provided
        if not data.get('payment_date'):
            data['payment_date'] = None  # Will use DEFAULT CURRENT_TIMESTAMP
            
        # Set default status if not provided
        if not data.get('status'):
            data['status'] = 'Pending'
            
        return self.db.execute_query(query, data)
    
    def update_payment(self, payment_id, data):
        query = """UPDATE Payment SET
                Amount = %(amount)s,
                Method = %(method)s,
                TransactionID = %(transaction_id)s,
                Status = %(status)s
                WHERE PaymentID = %(id)s"""
        data['id'] = payment_id
        return self.db.execute_query(query, data)
    
    def delete_payment(self, payment_id):
        query = "DELETE FROM Payment WHERE PaymentID = %s"
        return self.db.execute_query(query, (payment_id,))
    
    def search_payments(self, search_term):
        query = """
        SELECT p.*, b.PassengerID, pas.Name as PassengerName
        FROM Payment p
        JOIN Booking b ON p.BookingID = b.BookingID
        JOIN Passenger pas ON b.PassengerID = pas.PassengerID
        WHERE p.TransactionID LIKE %s OR p.Status LIKE %s OR 
              pas.Name LIKE %s OR p.Method LIKE %s
        ORDER BY p.PaymentDate DESC
        """
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern, search_pattern))
