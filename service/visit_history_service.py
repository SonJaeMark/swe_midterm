import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.db_conn import get_db_connection
from mysql.connector import Error

def record_diagnosis(appointment_id, diagnosis_text):
    """
    Records or updates the diagnosis for a specific visit associated with an appointment.
    """
    connection = get_db_connection()
    if not connection:
        return False

    success = False
    try:
        cursor = connection.cursor()
        query = "UPDATE visit_history SET diagnosis = %s WHERE appointment_id = %s"
        cursor.execute(query, (diagnosis_text, appointment_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Diagnosis recorded successfully for appointment ID {appointment_id}.")
            success = True
        else:
            print(f"No visit history record found for appointment ID {appointment_id}.")
    except Error as e:
        print(f"Error recording diagnosis: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return success

def record_prescription(appointment_id, prescription_text):
    """
    Records or updates the prescription details for a specific visit associated with an appointment.
    """
    connection = get_db_connection()
    if not connection:
        return False

    success = False
    try:
        cursor = connection.cursor()
        query = "UPDATE visit_history SET prescription = %s WHERE appointment_id = %s"
        cursor.execute(query, (prescription_text, appointment_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Prescription recorded successfully for appointment ID {appointment_id}.")
            success = True
        else:
            print(f"No visit history record found for appointment ID {appointment_id}.")
    except Error as e:
        print(f"Error recording prescription: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return success

def view_history(patient_id):
    """
    Retrieves the complete visit history for a specific patient, ordered by the most recent visit date.
    """
    connection = get_db_connection()
    if not connection:
        return []

    history = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT v.*, 
                   CONCAT(m.first_name, ' ', m.last_name) AS doctor_name, 
                   m.specialty
            FROM visit_history v
            JOIN medical_staff m ON v.staff_id = m.staff_id
            WHERE v.patient_id = %s
            ORDER BY v.visit_date DESC
        """
        cursor.execute(query, (patient_id,))
        history = cursor.fetchall()
    except Error as e:
        print(f"Error fetching visit history for patient ID {patient_id}: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return history

def view_history_by_doctor(staff_id):
    """Returns completed visit history recorded by one doctor, newest first."""
    connection = get_db_connection()
    if not connection:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT v.*, p.first_name AS patient_first_name,
                   p.last_name AS patient_last_name, a.queue_number
            FROM visit_history v
            JOIN patients p ON p.patient_id = v.patient_id
            JOIN appointments a ON a.appointment_id = v.appointment_id
            WHERE v.staff_id = %s
            ORDER BY v.visit_date DESC, v.visit_id DESC
            """,
            (staff_id,)
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching visit history for doctor ID {staff_id}: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_visit_record(appointment_id, patient_id, staff_id, diagnosis=None, prescription=None):
    """
    Initializes a new visit history entry when an appointment begins or concludes.
    Returns the new visit_id if successful, else None.
    """
    connection = get_db_connection()
    if not connection:
        return None

    visit_id = None
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO visit_history (appointment_id, patient_id, staff_id, diagnosis, prescription)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                diagnosis = COALESCE(%s, diagnosis), 
                prescription = COALESCE(%s, prescription)
        """
        cursor.execute(query, (appointment_id, patient_id, staff_id, diagnosis, prescription, diagnosis, prescription))
        connection.commit()
        visit_id = cursor.lastrowid if cursor.lastrowid else appointment_id
        print(f"Visit history record processed successfully.")
    except Error as e:
        print(f"Error creating/updating visit record: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return visit_id