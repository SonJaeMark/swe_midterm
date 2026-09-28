import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.db_conn import get_db_connection
from repository import user_repo, appointment_repo
from mysql.connector import Error
from datetime import datetime

def format_date_for_db(date_str):
    """Converts an entered date to YYYY-MM-DD for MySQL DATE columns."""
    if not date_str or date_str in ("MM/DD/YYYY", "MM-DD-YYYY"):
        return None
    for date_format in ("%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(date_str, date_format).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def get_available_doctors_for_date(date_str):
    """Returns doctors with at least one open appointment slot on the date."""
    appointment_date = format_date_for_db(date_str)
    if not appointment_date:
        return []
    return appointment_repo.get_doctors_with_available_slots(appointment_date)

def count_scheduled_appointments(patient_id):
    """Returns the patient's number of active scheduled appointments."""
    return appointment_repo.count_scheduled_appointments(patient_id)

def register_patient_account(username, email, password_hash, first_name, last_name, phone_number=None, date_of_birth=None, address=None):
    """
    Registers a new patient by creating a user account and their patient profile.
    Returns the newly created user_id, or None if failed.
    """
    formatted_dob = format_date_for_db(date_of_birth)
    
    return user_repo.register_patient(
        username=username,
        email=email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        date_of_birth=formatted_dob,
        address=address
    )

def view_profile(user_id):
    """
    Retrieves complete patient profile details associated with a given user_id.
    Returns a dictionary of patient details or None.
    """
    connection = get_db_connection()
    if not connection:
        return None

    patient_profile = None
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT p.*, u.username, u.email, u.role, u.created_at 
            FROM patients p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.user_id = %s
        """
        cursor.execute(query, (user_id,))
        patient_profile = cursor.fetchone()
    except Error as e:
        print(f"Error fetching patient profile: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return patient_profile

def update_profile(patient_id, first_name=None, last_name=None, phone_number=None, address=None):
    """
    Updates patient-specific profile information.
    Returns True if successful, else False.
    """
    connection = get_db_connection()
    if not connection:
        return False

    updates = []
    values = []

    if first_name is not None:
        updates.append("first_name = %s")
        values.append(first_name)
    if last_name is not None:
        updates.append("last_name = %s")
        values.append(last_name)
    if phone_number is not None:
        updates.append("phone_number = %s")
        values.append(phone_number)
    if address is not None:
        updates.append("address = %s")
        values.append(address)

    if not updates:
        print("No fields provided for patient profile update.")
        return False

    values.append(patient_id)
    success = False
    try:
        cursor = connection.cursor()
        query = f"UPDATE patients SET {', '.join(updates)} WHERE patient_id = %s"
        cursor.execute(query, tuple(values))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Successfully updated patient ID {patient_id}.")
            success = True
        else:
            print(f"No patient found with ID {patient_id}.")
    except Error as e:
        print(f"Error updating patient profile: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return success

def schedule_appointment(patient_id, staff_id, queue_number, appointment_date, appointment_time):
    """
    Schedules an appointment for the patient after checking doctor availability.
    Returns appointment_id if successful, else None.
    """
    return appointment_repo.create_appointment(
        patient_id=patient_id,
        staff_id=staff_id,
        queue_number=queue_number,
        appointment_date=appointment_date,
        appointment_time=appointment_time
    )

def track_queue(user_id, patient_id=None):
    """
    Retrieves the current active queue ticket for a patient user.
    Returns an appointment dictionary or None.
    """
    if patient_id is None:
        patient = view_profile(user_id)
        if not patient:
            return None
        patient_id = patient["patient_id"]
    return appointment_repo.get_current_queue_ticket_by_patient_id(patient_id)

def view_scheduled_appointments(patient_id):
    """
    Retrieves all scheduled appointments for a patient.
    Returns a list of appointment dictionaries.
    """
    return appointment_repo.get_all_appointments_is_scheduled_by_patient_id(patient_id)