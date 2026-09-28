import os
import mysql.connector
from mysql.connector import Error

def execute_sql_file(cursor, file_path):
    """
    Helper function to read and execute an SQL file statement by statement.
    """
    if not os.path.exists(file_path):
        print(f"Error: Could not find file at path: {file_path}")
        return False
    
    with open(file_path, 'r') as file:
        sql_script = file.read()
        
    statements = sql_script.split(';')
    for statement in statements:
        cleaned_statement = statement.strip()
        if cleaned_statement:
            cursor.execute(cleaned_statement)
            
    return True

def initialize_database():
    """
    Checks if mediqueue_db exists. If not, runs db.sql and dummy.sql.
    If it exists, skips dummy.sql.
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_sql_path = os.path.join(root_dir, 'db.sql')
    dummy_sql_path = os.path.join(root_dir, 'dummy.sql')

    connection = None
    cursor = None
    try:
        # Connect directly to the XAMPP MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Check if 'mediqueue_db' already exists
            cursor.execute("SHOW DATABASES LIKE 'mediqueue_db';")
            database_exists = cursor.fetchone() is not None

            if not database_exists:
                print("'mediqueue_db' does not exist. Setting up fresh database...")
                
                # 1. Execute db.sql to create database and tables
                print("Executing db.sql...")
                if not execute_sql_file(cursor, db_sql_path):
                    return False
                print("Successfully created database and tables from db.sql.")
                
                # 2. Execute dummy.sql since the database is new
                print("Executing dummy.sql for initial data...")
                if not execute_sql_file(cursor, dummy_sql_path):
                    return False
                print("Successfully populated database with dummy data.")
            else:
                print("'mediqueue_db' already exists. Skipping dummy.sql execution.")
                print("Verifying schema with db.sql...")
                if not execute_sql_file(cursor, db_sql_path):
                    return False

            connection.commit()
            print("Database initialization process finished successfully.")
            return True

    except Error as e:
        print(f"Error while initializing the database: {e}")
        return False
    except (OSError, UnicodeError) as e:
        print(f"Error reading database setup files: {e}")
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    initialize_database()