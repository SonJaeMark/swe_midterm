import os
import sys
from mysql.connector import Error

# Ensure the project root is in sys.path so 'config' can be imported correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.db_conn import get_db_connection

def register_patient(username, email, password_hash, first_name, last_name, phone_number=None, date_of_birth=None, address=None):
    """
    Registers a new patient by creating a user account with role 'PATIENT' 
    and adding their extended profile info into the 'patients' table.
    
    Parameters:
        username (str): The unique username of the user[cite: 2].
        email (str): The unique email of the user[cite: 2].
        password_hash (str): The hashed password string[cite: 2].
        first_name (str): Patient's first name[cite: 2].
        last_name (str): Patient's last name[cite: 2].
        phone_number (str, optional): Patient's contact number[cite: 2].
        date_of_birth (str/date, optional): Patient's DOB (YYYY-MM-DD)[cite: 2].
        address (str, optional): Patient's address[cite: 2].
        
    Returns:
        int: The user_id / patient profile creation success indicator, or None if failed.
    """
    connection = get_db_connection()
    if not connection:
        print("Error: Failed to establish a database connection.")
        return None

    user_id = None
    try:
        cursor = connection.cursor()
        
        # 1. Insert into the base 'users' table with role 'PATIENT'
        user_query = """
            INSERT INTO users (username, email, password_hash, role)
            VALUES (%s, %s, %s, 'PATIENT')
        """
        cursor.execute(user_query, (username, email, password_hash))
        user_id = cursor.lastrowid
        
        # 2. Insert into the extended 'patients' table using the new user_id
        patient_query = """
            INSERT INTO patients (user_id, first_name, last_name, phone_number, date_of_birth, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        patient_values = (user_id, first_name, last_name, phone_number, date_of_birth, address)
        cursor.execute(patient_query, patient_values)
        
        # Commit both inserts together
        connection.commit()
        print(f"Successfully registered patient '{first_name} {last_name}' with User ID {user_id}.")

    except Error as e:
        print(f"Error while registering patient in the database: {e}")
        connection.rollback()
        user_id = None
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return user_id

def get_user_details(user_id=None, username=None, email=None):
    """
    Retrieves user details from the 'users' table by user_id or username.
    
    Parameters:
        user_id (int, optional): The ID of the user.
        username (str, optional): The username of the user.
        email (str, optional): The email of the user.
        
    Returns:
        dict: A dictionary containing user details if found, else None.
    """
    connection = get_db_connection()
    if not connection:
        print("Error: Failed to establish a database connection.")
        return None

    user = None
    try:
        # Use dictionary=True to return rows as key-value pairs
        cursor = connection.cursor(dictionary=True)
        
        if user_id:
            query = "SELECT user_id, username, email, role, created_at FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
        elif username:
            query = "SELECT user_id, username, email, role, created_at FROM users WHERE username = %s"
            cursor.execute(query, (username,))
        elif email:
            query = "SELECT user_id, username, email, role, created_at FROM users WHERE email = %s"
            cursor.execute(query, (email,))
        else:
            print("Error: Either user_id, username, or email must be provided.")
            return None
            
        user = cursor.fetchone()

    except Error as e:
        print(f"Error while retrieving user details: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return user


def get_user_for_login(identifier):
    """Retrieves the credential fields needed to authenticate by email or username."""
    connection = get_db_connection()
    if not connection:
        print("Error: Failed to establish a database connection.")
        return None

    user = None
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT user_id, username, email, password_hash, role, created_at
            FROM users
            WHERE email = %s OR username = %s
            LIMIT 1
        """
        cursor.execute(query, (identifier, identifier))
        user = cursor.fetchone()

    except Error as e:
        print(f"Error while retrieving login details: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return user


def update_user_details(user_id, username=None, email=None, password_hash=None, role=None):
    """
    Updates user details dynamically in the 'users' table for a given user_id.
    
    Parameters:
        user_id (int): The ID of the user to update.
        username (str, optional): New username.
        email (str, optional): New email.
        password_hash (str, optional): New hashed password.
        role (str, optional): New role ('PATIENT', 'STAFF', or 'DOCTOR').
        
    Returns:
        bool: True if the update was successful, else False.
    """
    connection = get_db_connection()
    if not connection:
        print("Error: Failed to establish a database connection.")
        return False

    updates = []
    values = []

    if username is not None:
        updates.append("username = %s")
        values.append(username)
    if email is not None:
        updates.append("email = %s")
        values.append(email)
    if password_hash is not None:
        updates.append("password_hash = %s")
        values.append(password_hash)
    if role is not None:
        updates.append("role = %s")
        values.append(role)

    if not updates:
        print("Error: No fields provided for update.")
        return False

    values.append(user_id)
    success = False
    
    try:
        cursor = connection.cursor()
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        
        cursor.execute(query, tuple(values))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Successfully updated user ID {user_id}.")
            success = True
        else:
            print(f"No user found with ID {user_id} or no changes made.")

    except Error as e:
        print(f"Error while updating user details: {e}")
        connection.rollback()
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return success


if __name__ == "__main__":
    # Test block to verify functions
    print("Testing repository functions...")
    
    # 1. Test save_user
    print("Testing patient registration...")
    test_user_id = register_patient(
        username="janedoe",
        email="janedoe@example.com",
        password_hash="secure_hash_string_123",
        first_name="Jane",
        last_name="Doe",
        phone_number="555-0192",
        date_of_birth="1995-06-15",
        address="123 Health St, Clinic City"
    )
    print(f"Registration Result - User ID: {test_user_id}")

    if test_user_id:
        # 2. Test get_user_details
        print("\nTesting get_user_details...")
        details = get_user_details(user_id=test_user_id)
        print("Retrieved User:", details)
        
        # 3. Test update_user_details
        print("\nTesting update_user_details...")
        update_user_details(user_id=test_user_id, email="jane.new@example.com")
        
        updated_details = get_user_details(user_id=test_user_id)
        print("Updated User Details:", updated_details)