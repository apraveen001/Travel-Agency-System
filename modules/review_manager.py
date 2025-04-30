class ReviewManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_reviews(self):
        query = """
        SELECT r.*, b.PassengerID, p.Name as PassengerName
        FROM Review r
        JOIN Booking b ON r.BookingID = b.BookingID
        JOIN Passenger p ON b.PassengerID = p.PassengerID
        ORDER BY r.ReviewDate DESC
        """
        return self.db.fetch_all(query)
    
    def get_reviews_by_booking(self, booking_id):
        query = """
        SELECT r.*
        FROM Review r
        WHERE r.BookingID = %s
        """
        return self.db.fetch_all(query, (booking_id,))
    
    def get_review_by_id(self, review_id):
        query = """
        SELECT r.*, b.PassengerID, p.Name as PassengerName
        FROM Review r
        JOIN Booking b ON r.BookingID = b.BookingID
        JOIN Passenger p ON b.PassengerID = p.PassengerID
        WHERE r.ReviewID = %s
        """
        return self.db.fetch_one(query, (review_id,))
    
    def add_review(self, data):
        query = """INSERT INTO Review 
                (BookingID, Rating, Comment, ReviewDate)
                VALUES (%(booking_id)s, %(rating)s, %(comment)s, %(review_date)s)"""
        
        # Set default review date if not provided
        if not data.get('review_date'):
            data['review_date'] = None  # Will use DEFAULT CURRENT_DATE
            
        return self.db.execute_query(query, data)
    
    def update_review(self, review_id, data):
        query = """UPDATE Review SET
                Rating = %(rating)s,
                Comment = %(comment)s
                WHERE ReviewID = %(id)s"""
        data['id'] = review_id
        return self.db.execute_query(query, data)
    
    def delete_review(self, review_id):
        query = "DELETE FROM Review WHERE ReviewID = %s"
        return self.db.execute_query(query, (review_id,))
    
    def search_reviews(self, search_term):
        query = """
        SELECT r.*, b.PassengerID, p.Name as PassengerName
        FROM Review r
        JOIN Booking b ON r.BookingID = b.BookingID
        JOIN Passenger p ON b.PassengerID = p.PassengerID
        WHERE p.Name LIKE %s OR r.Comment LIKE %s
        ORDER BY r.ReviewDate DESC
        """
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern))
