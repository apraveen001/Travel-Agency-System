class CarRentalManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_car_rentals(self):
        query = """
        SELECT cr.*, 
               pickup.City as PickupCity, pickup.Country as PickupCountry,
               dropoff.City as DropoffCity, dropoff.Country as DropoffCountry
        FROM CarRental cr
        JOIN Location pickup ON cr.PickupLocationID = pickup.LocationID
        JOIN Location dropoff ON cr.DropoffLocationID = dropoff.LocationID
        ORDER BY cr.CarType
        """
        return self.db.fetch_all(query)
    
    def get_car_rental_by_id(self, rental_id):
        query = """
        SELECT cr.*, 
               pickup.City as PickupCity, pickup.Country as PickupCountry,
               dropoff.City as DropoffCity, dropoff.Country as DropoffCountry
        FROM CarRental cr
        JOIN Location pickup ON cr.PickupLocationID = pickup.LocationID
        JOIN Location dropoff ON cr.DropoffLocationID = dropoff.LocationID
        WHERE cr.RentalID = %s
        """
        return self.db.fetch_one(query, (rental_id,))
    
    def add_car_rental(self, data):
        query = """INSERT INTO CarRental 
                (CarType, DailyRate, PickupLocationID, DropoffLocationID)
                VALUES (%(car_type)s, %(daily_rate)s, %(pickup_location_id)s, %(dropoff_location_id)s)"""
        return self.db.execute_query(query, data)
    
    def update_car_rental(self, rental_id, data):
        query = """UPDATE CarRental SET
                CarType = %(car_type)s,
                DailyRate = %(daily_rate)s,
                PickupLocationID = %(pickup_location_id)s,
                DropoffLocationID = %(dropoff_location_id)s
                WHERE RentalID = %(id)s"""
        data['id'] = rental_id
        return self.db.execute_query(query, data)
    
    def delete_car_rental(self, rental_id):
        # Check for dependencies before deleting
        query = "SELECT COUNT(*) as count FROM BookingCarRental WHERE RentalID = %s"
        result = self.db.fetch_one(query, (rental_id,))
        if result and result['count'] > 0:
            return False
        
        query = "DELETE FROM CarRental WHERE RentalID = %s"
        return self.db.execute_query(query, (rental_id,))
    
    def search_car_rentals(self, search_term):
        query = """
        SELECT cr.*, 
               pickup.City as PickupCity, pickup.Country as PickupCountry,
               dropoff.City as DropoffCity, dropoff.Country as DropoffCountry
        FROM CarRental cr
        JOIN Location pickup ON cr.PickupLocationID = pickup.LocationID
        JOIN Location dropoff ON cr.DropoffLocationID = dropoff.LocationID
        WHERE cr.CarType LIKE %s OR 
              pickup.City LIKE %s OR pickup.Country LIKE %s OR
              dropoff.City LIKE %s OR dropoff.Country LIKE %s
        ORDER BY cr.CarType
        """
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
