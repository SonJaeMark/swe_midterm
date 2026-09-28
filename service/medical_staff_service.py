import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.db_conn import get_db_connection
from mysql.connector import Error

def get_medical_staff_by_user_id(user_id):
    """Returns the medical staff profile linked to a users-table ID."""
    connection = get_db_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT staff_id, user_id, first_name, last_name, specialty
            FROM medical_staff
            WHERE user_id = %s
            LIMIT 1
            """,
            (user_id,)
        )
        return cursor.fetchone()
    except Error as e:
        print(f"Error retrieving medical staff profile: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_available_doctors():
    """Returns active doctor profiles for appointment reassignment."""
    connection = get_db_connection()
    if not connection:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT m.staff_id, m.first_name, m.last_name, m.specialty
            FROM medical_staff m
            JOIN users u ON u.user_id = m.user_id
            WHERE m.available = TRUE AND u.role = 'DOCTOR'
            ORDER BY m.first_name, m.last_name
            """
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error retrieving doctors: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def has_in_progress_appointment(staff_id):
    """Returns whether a doctor has an appointment currently in progress, or None on failure."""
    connection = get_db_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT 1 FROM appointments WHERE staff_id = %s AND status = 'IN_PROGRESS' LIMIT 1",
            (staff_id,)
        )
        return cursor.fetchone() is not None
    except Error as e:
        print(f"Error checking in-progress appointments: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def view_daily_queue(staff_id, appointment_date=None):
    """
    Retrieves the daily queue of appointments assigned to a specific medical staff member.
    """
    connection = get_db_connection()
    if not connection:
        return []

    queue = []
    try:
        cursor = connection.cursor(dictionary=True)
        if appointment_date:
            query = """
                SELECT a.*, p.first_name AS patient_first_name, p.last_name AS patient_last_name 
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                WHERE a.staff_id = %s AND a.appointment_date = %s
                ORDER BY a.queue_number ASC
            """
            cursor.execute(query, (staff_id, appointment_date))
        else:
            query = """
                SELECT a.*, p.first_name AS patient_first_name, p.last_name AS patient_last_name 
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                WHERE a.staff_id = %s AND a.status NOT IN ('CANCELLED', 'COMPLETED')
                ORDER BY a.queue_number ASC
            """
            cursor.execute(query, (staff_id,))
            
        queue = cursor.fetchall()
    except Error as e:
        print(f"Error fetching daily queue: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return queue

def assign_doctor(appointment_id, new_staff_id):
    """
    Reassigns an appointment to a different medical staff member/doctor.
    """
    connection = get_db_connection()
    if not connection:
        return False

    success = False
    try:
        cursor = connection.cursor()
        query = "UPDATE appointments SET staff_id = %s WHERE appointment_id = %s"
        cursor.execute(query, (new_staff_id, appointment_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Successfully reassigned appointment ID {appointment_id} to staff ID {new_staff_id}.")
            success = True
        else:
            print(f"No appointment found with ID {appointment_id}.")
    except Error as e:
        print(f"Error assigning doctor: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return success

def call_next_patient(staff_id):
    """
    Updates the status of the next scheduled patient in the queue to 'IN_PROGRESS' (or 'CALLED').
    """
    connection = get_db_connection()
    if not connection:
        return None

    called_appointment = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT staff_id FROM medical_staff WHERE staff_id = %s FOR UPDATE", (staff_id,))
        if not cursor.fetchone():
            return None

        cursor.execute(
            "SELECT appointment_id FROM appointments WHERE staff_id = %s AND status = 'IN_PROGRESS' LIMIT 1",
            (staff_id,)
        )
        if cursor.fetchone():
            print("Cannot call next patient while another appointment is in progress.")
            return None

        # Queue tokens are identifiers, not sequence numbers; use appointment time for ordering.
        select_query = """
            SELECT appointment_id, queue_number FROM appointments
            WHERE staff_id = %s AND status IN ('SCHEDULED', 'IN_QUEUE')
            ORDER BY appointment_date ASC, appointment_time ASC, created_at ASC, appointment_id ASC
            LIMIT 1 FOR UPDATE
        """
        cursor.execute(select_query, (staff_id,))
        next_apt = cursor.fetchone()

        if next_apt:
            apt_id = next_apt['appointment_id']
            update_query = """
                UPDATE appointments SET status = 'IN_PROGRESS'
                WHERE appointment_id = %s AND status IN ('SCHEDULED', 'IN_QUEUE')
            """
            cursor.execute(update_query, (apt_id,))
            if cursor.rowcount == 0:
                connection.rollback()
                return None
            cursor.execute(
                """
                SELECT a.*, p.first_name AS patient_first_name,
                       p.last_name AS patient_last_name, p.phone_number AS patient_phone,
                       p.date_of_birth AS patient_date_of_birth
                FROM appointments a
                JOIN patients p ON p.patient_id = a.patient_id
                WHERE a.appointment_id = %s
                """,
                (apt_id,)
            )
            called_appointment = cursor.fetchone()
            connection.commit()
            print(f"Called next patient with appointment ID {apt_id} (Queue: {next_apt['queue_number']}).")
        else:
            print("No pending patients in the queue.")
    except Error as e:
        print(f"Error calling next patient: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return called_appointment

def complete_consultation(appointment_id, staff_id, diagnosis, prescription):
    """Completes this doctor's active appointment and records its visit history atomically."""
    connection = get_db_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT patient_id, staff_id FROM appointments
            WHERE appointment_id = %s AND staff_id = %s AND status = 'IN_PROGRESS'
            FOR UPDATE
            """,
            (appointment_id, staff_id)
        )
        appointment = cursor.fetchone()
        if not appointment:
            return False

        cursor.execute(
            "UPDATE appointments SET status = 'COMPLETED' WHERE appointment_id = %s",
            (appointment_id,)
        )
        cursor.execute(
            """
            INSERT INTO visit_history (appointment_id, patient_id, staff_id, diagnosis, prescription)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE diagnosis = %s, prescription = %s
            """,
            (
                appointment_id, appointment["patient_id"], staff_id, diagnosis, prescription,
                diagnosis, prescription
            )
        )
        connection.commit()
        return True
    except Error as e:
        print(f"Error completing consultation: {e}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def start_consultation(appointment_id):
    """
    Starts the consultation session by ensuring the appointment status is 'IN_PROGRESS'.
    """
    connection = get_db_connection()
    if not connection:
        return False

    success = False
    try:
        cursor = connection.cursor()
        query = "UPDATE appointments SET status = 'IN_PROGRESS' WHERE appointment_id = %s"
        cursor.execute(query, (appointment_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Consultation started for appointment ID {appointment_id}.")
            success = True
    except Error as e:
        print(f"Error starting consultation: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return success

def enter_diagnosis(appointment_id, diagnosis_text):
    """
    Records or updates the diagnosis for a patient's visit or appointment record.
    """
    connection = get_db_connection()
    if not connection:
        return False

    success = False
    try:
        cursor = connection.cursor()
        # Assumes a 'diagnosis' column exists in your appointments or medical records table
        query = "UPDATE appointments SET diagnosis = %s WHERE appointment_id = %s"
        cursor.execute(query, (diagnosis_text, appointment_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Diagnosis saved successfully for appointment ID {appointment_id}.")
            success = True
        else:
            print(f"Appointment ID {appointment_id} not found.")
    except Error as e:
        print(f"Error entering diagnosis: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return success

def enter_prescription(appointment_id, prescription_text):
    """
    Records or updates the prescription details for an appointment.
    """
    connection = get_db_connection()
    if not connection:
        return False

    success = False
    try:
        cursor = connection.cursor()
        # Assumes a 'prescription' column exists in your appointments table
        query = "UPDATE appointments SET prescription = %s WHERE appointment_id = %s"
        cursor.execute(query, (prescription_text, appointment_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Prescription saved successfully for appointment ID {appointment_id}.")
            success = True
        else:
            print(f"Appointment ID {appointment_id} not found.")
    except Error as e:
        print(f"Error entering prescription: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return success

def complete_appointment(appointment_id):
    """
    Marks the appointment status as 'COMPLETED'.
    """
    connection = get_db_connection()
    if not connection:
        return False

    success = False
    try:
        cursor = connection.cursor()
        query = "UPDATE appointments SET status = 'COMPLETED' WHERE appointment_id = %s"
        cursor.execute(query, (appointment_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Appointment ID {appointment_id} marked as COMPLETED.")
            success = True
    except Error as e:
        print(f"Error completing appointment: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return success

def search_patient_record(search_query):
    """
    Searches patient records by name, ID, or phone number.
    """
    connection = get_db_connection()
    if not connection:
        return []

    patients = []
    try:
        cursor = connection.cursor(dictionary=True)
        search_term = f"%{search_query}%"
        query = """
            SELECT p.*, u.email, u.username 
            FROM patients p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.first_name LIKE %s 
               OR p.last_name LIKE %s 
               OR p.phone_number LIKE %s 
               OR p.patient_id = %s
        """
        # If search_query is purely numeric, pass it for patient_id comparison as well
        patient_id_val = int(search_query) if search_query.isdigit() else -1
        cursor.execute(query, (search_term, search_term, search_term, patient_id_val))
        patients = cursor.fetchall()
    except Error as e:
        print(f"Error searching patient records: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return patients