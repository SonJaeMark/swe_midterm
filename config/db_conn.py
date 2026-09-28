import mysql.connector
from mysql.connector import Error

# Database configuration settings for XAMPP MySQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'mediqueue_db',  # Update with your actual database name if different
    'user': 'root',              # Default XAMPP MySQL username
    'password': ''               # Default XAMPP MySQL password is usually empty
}

def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to the MediQueue database.")
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        
    return connection

if __name__ == "__main__":
    # Test the connection when running this file directly
    conn = get_db_connection()
    if conn and conn.is_connected():
        conn.close()
        print("Database connection closed successfully.")