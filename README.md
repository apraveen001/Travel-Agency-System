# Travel Agency System

A comprehensive database management system for travel agencies to manage bookings, passengers, accommodations, and transportation options.

## Project Overview

This Travel Agency System is a full-featured web application built with Flask and MySQL that provides travel agencies with tools to manage their entire booking workflow. The system handles passenger information, accommodations, various transportation options (flights, car rentals, cruises), and booking management through an intuitive web interface.

The project implements a relational database with complex relationships between entities, transaction management, and business logic specific to the travel industry. It features a responsive web interface for data entry, visualization, and management.

## Features

- **Comprehensive Database Schema**: Fully normalized database design with 14 interconnected tables
- **Multi-entity Management**:
  - Passenger profiles and booking history
  - Accommodation options (hotels, resorts, etc.)
  - Transportation options (flights, car rentals, cruises)
  - Employee records and performance tracking
  - Payment processing and review management
- **Transaction Support**: Handles complex booking transactions with multiple components
- **Data Visualization**: View and analyze booking data, popular destinations, and employee performance
- **SQL Interface**: Direct SQL query execution for advanced operations
- **Entity Relationship Model**: Complete EER diagram documenting database structure
- **Data Generation**: Includes scripts to populate the database with realistic sample data

## Technology Stack

- **Backend**: Python with Flask framework
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: HTML, CSS, Jinja2 templates
- **Data Generation**: Python with Faker library

## Setup Instructions

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Travel-Agency-System.git
   cd Travel-Agency-System
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure MySQL:
   - Create a MySQL database named `travel_agency_db`
   - Update database connection parameters in `src/database.py` if needed

5. Initialize the database:
   ```
   mysql -u your_username -p travel_agency_db < sql/create_schema_mysql.sql
   mysql -u your_username -p travel_agency_db < sql/populate_data_mysql.sql
   ```

   Alternatively, you can use the web interface to view and execute the SQL scripts.

6. Run the application:
   ```
   python src/main.py
   ```

7. Access the application at `http://localhost:5000`

## Usage Guide

### Main Features

1. **View Database Schema**: Examine the database structure and relationships
2. **Manage Passengers**: Add, view, and update passenger information
3. **View Available Options**: Browse accommodations and transportation options
4. **Manage Bookings**: Create and track bookings with multiple components
5. **Execute Custom SQL**: Run custom queries for advanced operations
6. **View Passenger Itineraries**: See complete travel plans for each passenger

### Sample Workflow

1. Add a new passenger through the "Add Passenger" interface
2. Browse available accommodations and transportation options
3. Create a new booking for the passenger
4. Add accommodation and transportation details to the booking
5. View the complete itinerary for the passenger

## Database Structure

The database consists of 14 interconnected tables:

- **Core Entities**: Location, Passenger, Employee, Accommodation
- **Transportation Options**: Flight, CarRental, Cruise, TransportationType
- **Booking Management**: Booking, BookingPassenger, BookingAccommodation, BookingTransportation
- **Financial & Feedback**: Payment, Review

The EER diagram (`EER-Diagram.pdf`) provides a visual representation of these relationships.

## Complex Queries

The system includes several complex SQL queries demonstrating:

- Joining multiple tables for comprehensive reports
- Aggregation and grouping for statistical analysis
- Subqueries and advanced filtering
- Views for frequently accessed data combinations

Examples can be found in `sql/complex_queries.sql`.

## Data Generation

The project includes a data generation script (`generate_data.py`) that uses the Faker library to create realistic sample data for testing and demonstration purposes.

## Future Enhancements

Potential areas for expansion include:

- User authentication and role-based access control
- API endpoints for integration with other systems
- Advanced reporting and analytics features
- Mobile application support
- Integration with external booking systems and payment gateways

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Database design principles from Modern Database Management
- Flask web framework documentation and community
- MySQL documentation and best practices
