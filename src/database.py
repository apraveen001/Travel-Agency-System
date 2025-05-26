# -*- coding: utf-8 -*-
import os
from flask_sqlalchemy import SQLAlchemy
import mysql.connector # Import mysql connector
from mysql.connector import Error

db = SQLAlchemy()

# --- IMPORTANT: Placeholder MySQL connection details --- 
# --- The user MUST replace these with their actual credentials --- 
MYSQL_USER = "root" 
MYSQL_PASSWORD = "12345678"
MYSQL_HOST = "127.0.0.1" # Use 127.0.0.1 instead of localhost if connection issues arise
MYSQL_PORT = 3306 # Default MySQL port
DATABASE_NAME = "travel_agency_db" # Choose a database name
# --- End of Placeholder Credentials ---

def check_and_create_database():
    """Checks if the database exists on the MySQL server, creates it if not."""
    conn = None
    cursor = None
    try:
        # Connect to MySQL server (without specifying the database initially)
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port=MYSQL_PORT
        )
        conn.autocommit = True # Ensure commands like CREATE DATABASE are committed
        cursor = conn.cursor()
        
        # Check if the target database exists
        cursor.execute(f"SHOW DATABASES LIKE '{DATABASE_NAME}'")
        result = cursor.fetchone()
        
        if not result:
            print(f"Database '{DATABASE_NAME}' not found. Attempting to create...")
            # Use backticks for database name in CREATE statement for safety
            cursor.execute(f"CREATE DATABASE `{DATABASE_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{DATABASE_NAME}' created successfully.")
        else:
            print(f"Database '{DATABASE_NAME}' already exists.")
            
    except Error as e:
        print(f"Error during MySQL database check/creation: {e}")
        print("Please ensure MySQL server is running and credentials (user, password, host, port) are correct.")
        # Re-raise the exception to indicate failure
        raise RuntimeError(f"Failed to connect to MySQL or ensure database exists: {e}") from e
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("MySQL connection closed.")

def init_app(app):
    """Initialize the database connection for the Flask app using SQLAlchemy."""
    # First, ensure the database exists on the server
    try:
        check_and_create_database()
    except RuntimeError as e:
         # If database check/creation fails, log the error and potentially stop the app
         print(f"Critical error: {e}")
         # Optionally, you could raise a more specific exception or use Flask's logging
         # For now, we print and raise SystemExit to prevent the app from starting incorrectly
         raise SystemExit("Database setup failed. Please check MySQL connection and credentials.")

    # Configure SQLAlchemy to use the MySQL database
    # Ensure mysql-connector-python is installed: pip install mysql-connector-python
    # The mysql+mysqlconnector driver is recommended
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@" 
        f"{MYSQL_HOST}:{MYSQL_PORT}/{DATABASE_NAME}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # Recommended setting
    
    # Initialize SQLAlchemy with the Flask app instance
    db.init_app(app)

    # Note: MySQL generally handles foreign key constraints automatically if they are defined 
    # in the table schema (using InnoDB engine). The SQLite-specific PRAGMA is removed.

