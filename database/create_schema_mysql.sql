-- SQL Script to Create the Travel Agency Database Schema for MySQL
-- File: create_sql.sql

-- Create the database (optional - can be created separately)
CREATE DATABASE IF NOT EXISTS travel_agency_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE travel_agency_db;

-- Set default engine to InnoDB for foreign key support
SET default_storage_engine=InnoDB;

-- 1. Location Table
CREATE TABLE IF NOT EXISTS Location (
    LocationID INT PRIMARY KEY AUTO_INCREMENT,
    City VARCHAR(100) NOT NULL,
    State VARCHAR(100),
    Country VARCHAR(100) NOT NULL,
    INDEX idx_country (Country),
    INDEX idx_city (City)
);

-- 2. Passenger Table
CREATE TABLE IF NOT EXISTS Passenger (
    PassengerID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Gender ENUM('Male', 'Female', 'Other'),
    Age INT CHECK (Age > 0 AND Age < 120),
    Email VARCHAR(255) UNIQUE,
    Phone VARCHAR(20),
    INDEX idx_name (Name),
    INDEX idx_age (Age)
);

-- 3. Employee Table
CREATE TABLE IF NOT EXISTS Employee (
    EmployeeID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Role VARCHAR(100),
    JoinDate DATE,
    SupervisorID INT NULL,
    FOREIGN KEY (SupervisorID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL,
    INDEX idx_role (Role),
    INDEX idx_join_date (JoinDate)
);

-- 4. Accommodation Table
CREATE TABLE IF NOT EXISTS Accommodation (
    AccommodationID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Type ENUM('Hotel', 'Resort', 'Airbnb', 'Guesthouse', 'Inn', 'Suites'),
    Rate DECIMAL(10, 2) CHECK (Rate >= 0),
    Facilities TEXT,
    Discount DECIMAL(4, 2) DEFAULT 0.00 CHECK (Discount >= 0 AND Discount <= 1),
    LocationID INT NOT NULL,
    FOREIGN KEY (LocationID) REFERENCES Location(LocationID) ON DELETE CASCADE,
    INDEX idx_type (Type),
    INDEX idx_rate (Rate)
);

-- 5. TransportationType Table
CREATE TABLE IF NOT EXISTS TransportationType (
    TransportTypeID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL UNIQUE
);

-- Insert base transportation types
INSERT IGNORE INTO TransportationType (Name) VALUES 
('Flight'), ('Car Rental'), ('Bus'), ('Cruise'), ('Train'), ('Ferry');

-- 6. Flight Table
CREATE TABLE IF NOT EXISTS Flight (
    FlightID INT PRIMARY KEY AUTO_INCREMENT,
    FlightNumber VARCHAR(20) NOT NULL,
    Carrier VARCHAR(100) NOT NULL,
    SourceLocationID INT NOT NULL,
    DestLocationID INT NOT NULL,
    DepartureDateTime DATETIME NOT NULL,
    ArrivalDateTime DATETIME NOT NULL,
    Class ENUM('Economy', 'Premium Economy', 'Business', 'First'),
    Fare DECIMAL(10, 2) NOT NULL CHECK (Fare >= 0),
    FOREIGN KEY (SourceLocationID) REFERENCES Location(LocationID) ON DELETE CASCADE,
    FOREIGN KEY (DestLocationID) REFERENCES Location(LocationID) ON DELETE CASCADE,
    INDEX idx_flight_number (FlightNumber),
    INDEX idx_carrier (Carrier),
    INDEX idx_departure (DepartureDateTime)
);

-- 7. CarRental Table
CREATE TABLE IF NOT EXISTS CarRental (
    CarRentalID INT PRIMARY KEY AUTO_INCREMENT,
    Company VARCHAR(100) NOT NULL,
    CarType VARCHAR(100),
    PickupLocationID INT NOT NULL,
    DropoffLocationID INT NOT NULL,
    PickupDateTime DATETIME NOT NULL,
    DropoffDateTime DATETIME NOT NULL,
    Rent DECIMAL(10, 2) NOT NULL CHECK (Rent >= 0),
    FOREIGN KEY (PickupLocationID) REFERENCES Location(LocationID) ON DELETE CASCADE,
    FOREIGN KEY (DropoffLocationID) REFERENCES Location(LocationID) ON DELETE CASCADE,
    INDEX idx_company (Company),
    INDEX idx_pickup_date (PickupDateTime)
);

-- 8. Cruise Table
CREATE TABLE IF NOT EXISTS Cruise (
    CruiseID INT PRIMARY KEY AUTO_INCREMENT,
    CruiseName VARCHAR(255) NOT NULL,
    Line VARCHAR(100),
    SourceLocationID INT NOT NULL,
    DestLocationID INT NOT NULL,
    DepartureDate DATE NOT NULL,
    ReturnDate DATE NOT NULL,
    Fare DECIMAL(10, 2) NOT NULL CHECK (Fare >= 0),
    FOREIGN KEY (SourceLocationID) REFERENCES Location(LocationID) ON DELETE CASCADE,
    FOREIGN KEY (DestLocationID) REFERENCES Location(LocationID) ON DELETE CASCADE,
    INDEX idx_cruise_name (CruiseName),
    INDEX idx_departure_date (DepartureDate)
);

-- 9. Booking Table
CREATE TABLE IF NOT EXISTS Booking (
    BookingID INT PRIMARY KEY AUTO_INCREMENT,
    GroupName VARCHAR(255),
    Purpose ENUM('Leisure', 'Business', 'Family', 'Honeymoon', 'Adventure', 'Other'),
    BookingDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    EmployeeID INT NULL,
    TotalCost DECIMAL(12, 2) CHECK (TotalCost >= 0),
    Status ENUM('Pending', 'Confirmed', 'Cancelled', 'Completed') DEFAULT 'Pending',
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL,
    INDEX idx_booking_date (BookingDate),
    INDEX idx_purpose (Purpose)
);

-- 10. BookingPassenger Table (Many-to-Many linking Bookings and Passengers)
CREATE TABLE IF NOT EXISTS BookingPassenger (
    BookingID INT NOT NULL,
    PassengerID INT NOT NULL,
    IsPrimary BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (BookingID, PassengerID),
    FOREIGN KEY (BookingID) REFERENCES Booking(BookingID) ON DELETE CASCADE,
    FOREIGN KEY (PassengerID) REFERENCES Passenger(PassengerID) ON DELETE CASCADE
);

-- 11. BookingAccommodation Table
CREATE TABLE IF NOT EXISTS BookingAccommodation (
    BookingAccommodationID INT PRIMARY KEY AUTO_INCREMENT,
    BookingID INT NOT NULL,
    AccommodationID INT NOT NULL,
    CheckInDate DATE NOT NULL,
    CheckOutDate DATE NOT NULL,
    Cost DECIMAL(10, 2) CHECK (Cost >= 0),
    FOREIGN KEY (BookingID) REFERENCES Booking(BookingID) ON DELETE CASCADE,
    FOREIGN KEY (AccommodationID) REFERENCES Accommodation(AccommodationID) ON DELETE CASCADE,
    INDEX idx_check_in (CheckInDate)
);

-- 12. BookingTransportation Table
CREATE TABLE IF NOT EXISTS BookingTransportation (
    BookingTransportationID INT PRIMARY KEY AUTO_INCREMENT,
    BookingID INT NOT NULL,
    TransportTypeID INT NOT NULL,
    FlightID INT NULL,
    CarRentalID INT NULL,
    CruiseID INT NULL,
    Cost DECIMAL(10, 2) CHECK (Cost >= 0),
    FOREIGN KEY (BookingID) REFERENCES Booking(BookingID) ON DELETE CASCADE,
    FOREIGN KEY (TransportTypeID) REFERENCES TransportationType(TransportTypeID) ON DELETE CASCADE,
    FOREIGN KEY (FlightID) REFERENCES Flight(FlightID),
    FOREIGN KEY (CarRentalID) REFERENCES CarRental(CarRentalID),
    FOREIGN KEY (CruiseID) REFERENCES Cruise(CruiseID),
    CONSTRAINT chk_one_transport CHECK (
        (CASE WHEN FlightID IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN CarRentalID IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN CruiseID IS NOT NULL THEN 1 ELSE 0 END) = 1
    )
);

-- 13. Payment Table
CREATE TABLE IF NOT EXISTS Payment (
    PaymentID INT PRIMARY KEY AUTO_INCREMENT,
    BookingID INT NOT NULL,
    PaymentDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Amount DECIMAL(12, 2) NOT NULL CHECK (Amount > 0),
    PaymentType ENUM('Credit Card', 'Debit Card', 'Bank Transfer', 'Cash', 'Other'),
    CardLastFour VARCHAR(4),
    ExpiryDate VARCHAR(7), -- MM/YYYY format
    FOREIGN KEY (BookingID) REFERENCES Booking(BookingID) ON DELETE CASCADE,
    INDEX idx_payment_date (PaymentDate)
);

-- 14. Review Table
CREATE TABLE IF NOT EXISTS Review (
    ReviewID INT PRIMARY KEY AUTO_INCREMENT,
    BookingID INT NOT NULL,
    PassengerID INT NOT NULL,
    Rating INT NOT NULL CHECK (Rating >= 1 AND Rating <= 5),
    Text TEXT,
    ReviewDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (BookingID) REFERENCES Booking(BookingID) ON DELETE CASCADE,
    FOREIGN KEY (PassengerID) REFERENCES Passenger(PassengerID) ON DELETE CASCADE,
    UNIQUE KEY unique_booking_passenger (BookingID, PassengerID),
    INDEX idx_rating (Rating)
);

-- Create a view for popular destinations
CREATE OR REPLACE VIEW PopularDestinations AS
SELECT 
    l.Country, 
    l.City, 
    COUNT(b.BookingID) AS BookingCount,
    AVG(r.Rating) AS AverageRating
FROM Location l
JOIN Accommodation a ON l.LocationID = a.LocationID
JOIN BookingAccommodation ba ON a.AccommodationID = ba.AccommodationID
JOIN Booking b ON ba.BookingID = b.BookingID
LEFT JOIN Review r ON b.BookingID = r.BookingID
GROUP BY l.Country, l.City
ORDER BY BookingCount DESC, AverageRating DESC
LIMIT 20;

-- Create a view for employee performance
CREATE OR REPLACE VIEW EmployeePerformance AS
SELECT 
    e.EmployeeID,
    e.Name,
    e.Role,
    COUNT(b.BookingID) AS TotalBookings,
    SUM(b.TotalCost) AS TotalRevenue,
    AVG(r.Rating) AS AverageRating
FROM Employee e
LEFT JOIN Booking b ON e.EmployeeID = b.EmployeeID
LEFT JOIN Review r ON b.BookingID = r.BookingID
GROUP BY e.EmployeeID, e.Name, e.Role
ORDER BY TotalRevenue DESC;

-- Add stored procedure for monthly report
DELIMITER //
CREATE PROCEDURE GenerateMonthlyReport(IN year INT, IN month INT)
BEGIN
    SELECT 
        b.BookingID,
        b.GroupName,
        b.BookingDate,
        b.TotalCost,
        p.Name AS PrimaryPassenger,
        e.Name AS AgentName
    FROM Booking b
    JOIN (
        SELECT bp.BookingID, p.Name
        FROM BookingPassenger bp
        JOIN Passenger p ON bp.PassengerID = p.PassengerID
        WHERE bp.IsPrimary = TRUE
    ) p ON b.BookingID = p.BookingID
    LEFT JOIN Employee e ON b.EmployeeID = e.EmployeeID
    WHERE YEAR(b.BookingDate) = year AND MONTH(b.BookingDate) = month
    ORDER BY b.TotalCost DESC;
END //
DELIMITER ;

-- Add trigger for booking total cost calculation
DELIMITER //
CREATE TRIGGER CalculateBookingTotal
AFTER INSERT ON BookingAccommodation
FOR EACH ROW
BEGIN
    DECLARE total DECIMAL(12, 2);
    
    -- Calculate accommodation costs
    SELECT SUM(Cost) INTO total
    FROM BookingAccommodation
    WHERE BookingID = NEW.BookingID;
    
    -- Add transportation costs
    SELECT total + IFNULL(SUM(Cost), 0) INTO total
    FROM BookingTransportation
    WHERE BookingID = NEW.BookingID;
    
    -- Update booking total
    UPDATE Booking
    SET TotalCost = total
    WHERE BookingID = NEW.BookingID;
END //
DELIMITER ;

-- Add similar trigger for transportation
DELIMITER //
CREATE TRIGGER CalculateBookingTotalTransport
AFTER INSERT ON BookingTransportation
FOR EACH ROW
BEGIN
    DECLARE total DECIMAL(12, 2);
    
    -- Calculate transportation costs
    SELECT SUM(Cost) INTO total
    FROM BookingTransportation
    WHERE BookingID = NEW.BookingID;
    
    -- Add accommodation costs
    SELECT total + IFNULL(SUM(Cost), 0) INTO total
    FROM BookingAccommodation
    WHERE BookingID = NEW.BookingID;
    
    -- Update booking total
    UPDATE Booking
    SET TotalCost = total
    WHERE BookingID = NEW.BookingID;
END //
DELIMITER ;

-- Create indexes for performance
CREATE INDEX idx_accommodation_location ON Accommodation(LocationID);
CREATE INDEX idx_flight_source ON Flight(SourceLocationID);
CREATE INDEX idx_flight_dest ON Flight(DestLocationID);
CREATE INDEX idx_cruise_source ON Cruise(SourceLocationID);
CREATE INDEX idx_cruise_dest ON Cruise(DestLocationID);
CREATE INDEX idx_car_pickup ON CarRental(PickupLocationID);
CREATE INDEX idx_car_dropoff ON CarRental(DropoffLocationID);
CREATE INDEX idx_booking_employee ON Booking(EmployeeID);