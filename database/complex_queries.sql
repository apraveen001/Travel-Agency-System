--1. Top 5 Most Popular Destinations by Booking Count
SELECT 
    l.Country, 
    l.City, 
    COUNT(ba.BookingAccommodationID) AS BookingCount,
    AVG(a.Rate) AS AverageRate
FROM Location l
JOIN Accommodation a ON l.LocationID = a.LocationID
JOIN BookingAccommodation ba ON a.AccommodationID = ba.AccommodationID
GROUP BY l.Country, l.City
ORDER BY BookingCount DESC
LIMIT 5;

--2. Employee Performance Analysis with Supervisor Information
SELECT 
    e.EmployeeID,
    e.Name AS EmployeeName,
    e.Role,
    COUNT(b.BookingID) AS TotalBookings,
    SUM(b.TotalCost) AS TotalRevenue,
    s.Name AS SupervisorName
FROM Employee e
LEFT JOIN Booking b ON e.EmployeeID = b.EmployeeID
LEFT JOIN Employee s ON e.SupervisorID = s.EmployeeID
GROUP BY e.EmployeeID, e.Name, e.Role, s.Name
ORDER BY TotalRevenue DESC;

--3. High-Value Customers (Passengers with Most Bookings and Highest Spending)
SELECT 
    p.PassengerID,
    p.Name,
    p.Email,
    COUNT(DISTINCT bp.BookingID) AS TotalBookings,
    SUM(b.TotalCost) AS TotalSpent,
    AVG(r.Rating) AS AverageRatingGiven
FROM Passenger p
JOIN BookingPassenger bp ON p.PassengerID = bp.PassengerID
JOIN Booking b ON bp.BookingID = b.BookingID
LEFT JOIN Review r ON b.BookingID = r.BookingID AND p.PassengerID = r.PassengerID
GROUP BY p.PassengerID, p.Name, p.Email
ORDER BY TotalSpent DESC
LIMIT 10;

--4. Seasonal Booking Trends by Purpose
SELECT 
    MONTH(b.BookingDate) AS Month,
    b.Purpose,
    COUNT(b.BookingID) AS BookingCount,
    SUM(b.TotalCost) AS TotalRevenue,
    AVG(b.TotalCost) AS AverageBookingValue
FROM Booking b
GROUP BY MONTH(b.BookingDate), b.Purpose
ORDER BY Month, BookingCount DESC;

--5. Transportation Type Analysis with Cost Comparison
SELECT 
    tt.Name AS TransportType,
    COUNT(bt.BookingTransportationID) AS BookingCount,
    AVG(bt.Cost) AS AverageCost,
    MIN(bt.Cost) AS MinCost,
    MAX(bt.Cost) AS MaxCost,
    SUM(bt.Cost) AS TotalRevenue
FROM BookingTransportation bt
JOIN TransportationType tt ON bt.TransportTypeID = tt.TransportTypeID
GROUP BY tt.Name
ORDER BY BookingCount DESC;

--6. Accommodation Performance by Type and Location
SELECT 
    a.Type,
    l.Country,
    l.City,
    COUNT(ba.BookingAccommodationID) AS BookingCount,
    AVG(ba.Cost) AS AverageRevenue,
    AVG(DATEDIFF(ba.CheckOutDate, ba.CheckInDate)) AS AverageStayDuration,
    AVG(r.Rating) AS AverageRating
FROM Accommodation a
JOIN Location l ON a.LocationID = l.LocationID
JOIN BookingAccommodation ba ON a.AccommodationID = ba.AccommodationID
LEFT JOIN Booking b ON ba.BookingID = b.BookingID
LEFT JOIN Review r ON b.BookingID = r.BookingID
GROUP BY a.Type, l.Country, l.City
ORDER BY BookingCount DESC;

--7. Cross-Selling Opportunities (Customers Who Booked One Service But Not Others)
SELECT 
    p.PassengerID,
    p.Name,
    GROUP_CONCAT(DISTINCT 
        CASE 
            WHEN tt.Name IS NOT NULL THEN tt.Name 
            ELSE 'None' 
        END
    ) AS TransportTypesUsed,
    GROUP_CONCAT(DISTINCT a.Type) AS AccommodationTypesUsed
FROM Passenger p
JOIN BookingPassenger bp ON p.PassengerID = bp.PassengerID
LEFT JOIN Booking b ON bp.BookingID = b.BookingID
LEFT JOIN BookingTransportation bt ON b.BookingID = bt.BookingID
LEFT JOIN TransportationType tt ON bt.TransportTypeID = tt.TransportTypeID
LEFT JOIN BookingAccommodation ba ON b.BookingID = ba.BookingID
LEFT JOIN Accommodation a ON ba.AccommodationID = a.AccommodationID
GROUP BY p.PassengerID, p.Name
ORDER BY p.Name;

--8. Revenue Growth Analysis by Quarter
SELECT 
    YEAR(b.BookingDate) AS Year,
    QUARTER(b.BookingDate) AS Quarter,
    COUNT(b.BookingID) AS BookingCount,
    SUM(b.TotalCost) AS TotalRevenue,
    SUM(b.TotalCost) - LAG(SUM(b.TotalCost), 1, 0) OVER (ORDER BY YEAR(b.BookingDate), QUARTER(b.BookingDate)) AS RevenueGrowth,
    ROUND((SUM(b.TotalCost) - LAG(SUM(b.TotalCost), 1, 0) OVER (ORDER BY YEAR(b.BookingDate), QUARTER(b.BookingDate))) / 
    NULLIF(LAG(SUM(b.TotalCost), 1, 0) OVER (ORDER BY YEAR(b.BookingDate), QUARTER(b.BookingDate)), 0) * 100, 2) AS GrowthPercentage
FROM Booking b
GROUP BY YEAR(b.BookingDate), QUARTER(b.BookingDate)
ORDER BY Year, Quarter;

--9. Customer Demographics Analysis

SELECT 
    p.Gender,
    CASE 
        WHEN p.Age < 20 THEN 'Teen'
        WHEN p.Age BETWEEN 20 AND 29 THEN '20s'
        WHEN p.Age BETWEEN 30 AND 39 THEN '30s'
        WHEN p.Age BETWEEN 40 AND 49 THEN '40s'
        WHEN p.Age BETWEEN 50 AND 59 THEN '50s'
        WHEN p.Age >= 60 THEN '60+'
    END AS AgeGroup,
    COUNT(DISTINCT p.PassengerID) AS CustomerCount,
    COUNT(DISTINCT bp.BookingID) AS BookingCount,
    AVG(b.TotalCost) AS AverageSpending,
    AVG(r.Rating) AS AverageRating
FROM Passenger p
LEFT JOIN BookingPassenger bp ON p.PassengerID = bp.PassengerID
LEFT JOIN Booking b ON bp.BookingID = b.BookingID
LEFT JOIN Review r ON b.BookingID = r.BookingID AND p.PassengerID = r.PassengerID
GROUP BY p.Gender, AgeGroup
ORDER BY Gender, AgeGroup;

--10. Booking Funnel Analysis (From Booking to Payment to Review)

SELECT 
    b.Status AS BookingStatus,
    COUNT(b.BookingID) AS TotalBookings,
    SUM(CASE WHEN p.PaymentID IS NOT NULL THEN 1 ELSE 0 END) AS PaidBookings,
    SUM(CASE WHEN r.ReviewID IS NOT NULL THEN 1 ELSE 0 END) AS ReviewedBookings,
    ROUND(SUM(CASE WHEN p.PaymentID IS NOT NULL THEN 1 ELSE 0 END) / COUNT(b.BookingID) * 100, 2) AS PaymentConversionRate,
    ROUND(SUM(CASE WHEN r.ReviewID IS NOT NULL THEN 1 ELSE 0 END) / COUNT(b.BookingID) * 100, 2) AS ReviewConversionRate,
    AVG(r.Rating) AS AverageRating
FROM Booking b
LEFT JOIN Payment p ON b.BookingID = p.BookingID
LEFT JOIN Review r ON b.BookingID = r.BookingID
GROUP BY b.Status
ORDER BY TotalBookings DESC;