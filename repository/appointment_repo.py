import os
import sys
from mysql.connector import Error

# Ensure the project root is in sys.path so 'config' can be imported correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.db_conn import get_db_connection

def check_appointment_if_possible(staff_id, appointment_date, appointment_time):
    """
    Checks if a doctor/staff is available and free at the specified date and time.
    Returns True if possible (no overlapping appointments), else False.
    """
    connection = get_db_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor(dictionary=True)
        # Check if there's already an active appointment for this doctor at the exact same date and time
        query = """
            SELECT appointment_id FROM appointments 
            WHERE staff_id = %s 
              AND appointment_date = %s 
              AND appointment_time = %s 
              AND status NOT IN ('CANCELLED', 'COMPLETED')
        """
        cursor.execute(query, (staff_id, appointment_date, appointment_time))
        result = cursor.fetchone()
        
        # If result is None, the slot is free
        return result is None

    except Error as e:
        print(f"Error checking appointment availability: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_appointment(patient_id, staff_id, queue_number, appointment_date, appointment_time):
    """
    Creates a new appointment after checking if the doctor's slot is available.
    Returns appointment_id if successful, else None.
    """
    connection = get_db_connection()
    if not connection:
        return None

    appointment_id = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT patient_id FROM patients WHERE patient_id = %s FOR UPDATE", (patient_id,))
        if not cursor.fetchone():
            return None

        cursor.execute(
            "SELECT COUNT(*) AS scheduled_count FROM appointments WHERE patient_id = %s AND status = 'SCHEDULED'",
            (patient_id,)
        )
        if cursor.fetchone()["scheduled_count"] >= 3:
            print("Error: Patient already has three scheduled appointments.")
            return None

        cursor.execute("SELECT staff_id FROM medical_staff WHERE staff_id = %s AND available = TRUE FOR UPDATE", (staff_id,))
        if not cursor.fetchone():
            return None

        cursor.execute(
            """
            SELECT appointment_id FROM appointments
            WHERE staff_id = %s AND appointment_date = %s AND appointment_time = %s
              AND status NOT IN ('CANCELLED', 'COMPLETED')
            """,
            (staff_id, appointment_date, appointment_time)
        )
        if cursor.fetchone():
            print("Error: The requested appointment slot is not available for this doctor.")
            return None

        query = """
            INSERT INTO appointments (patient_id, staff_id, queue_number, appointment_date, appointment_time, status)
            VALUES (%s, %s, %s, %s, %s, 'SCHEDULED')
        """
        values = (patient_id, staff_id, queue_number, appointment_date, appointment_time)
        
        cursor.execute(query, values)
        connection.commit()
        appointment_id = cursor.lastrowid
        print(f"Successfully created appointment with ID {appointment_id} (Queue: {queue_number}).")

    except Error as e:
        print(f"Error while creating appointment: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return appointment_id

def count_scheduled_appointments(patient_id):
    """Returns the number of SCHEDULED appointments for a patient, or None on failure."""
    connection = get_db_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT COUNT(*) AS scheduled_count FROM appointments WHERE patient_id = %s AND status = 'SCHEDULED'",
            (patient_id,)
        )
        return cursor.fetchone()["scheduled_count"]
    except Error as e:
        print(f"Error counting scheduled appointments: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_doctors_with_available_slots(appointment_date):
    """Returns available doctors and their open fixed-time slots for one date."""
    appointment_slots = ("10:00:00", "12:00:00", "15:00:00", "17:00:00")
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
        doctors = cursor.fetchall()
        cursor.execute(
            """
            SELECT staff_id, CAST(appointment_time AS CHAR) AS appointment_time
            FROM appointments
            WHERE appointment_date = %s
              AND status NOT IN ('CANCELLED', 'COMPLETED')
              AND staff_id IS NOT NULL
            """,
            (appointment_date,)
        )
        booked_slots = {}
        for appointment in cursor.fetchall():
            booked_slots.setdefault(appointment["staff_id"], set()).add(appointment["appointment_time"])

        available_doctors = []
        for doctor in doctors:
            doctor["available_slots"] = [
                slot for slot in appointment_slots
                if slot not in booked_slots.get(doctor["staff_id"], set())
            ]
            if doctor["available_slots"]:
                available_doctors.append(doctor)
        return available_doctors
    except Error as e:
        print(f"Error retrieving doctors with available slots: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def cancel_appointment(appointment_id):
    """
    Cancels an existing appointment by changing its status to 'CANCELLED'.
    Returns True if successful, else False.
    """
    connection = get_db_connection()
    if not connection:
        return False

    success = False
    try:
        cursor = connection.cursor()
        query = "UPDATE appointments SET status = 'CANCELLED' WHERE appointment_id = %s"
        cursor.execute(query, (appointment_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Successfully cancelled appointment ID {appointment_id}.")
            success = True
        else:
            print(f"No appointment found with ID {appointment_id}.")

    except Error as e:
        print(f"Error while cancelling appointment: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return success

def cancel_appointment_by_queue_number(queue_number):
    """Cancels an active appointment identified by its queue number."""
    connection = get_db_connection()
    if not connection:
        return False

    success = False
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE appointments
            SET status = 'CANCELLED'
            WHERE queue_number = %s
              AND status IN ('SCHEDULED', 'IN_QUEUE', 'IN_PROGRESS')
            """,
            (queue_number,)
        )
        connection.commit()
        success = cursor.rowcount > 0
    except Error as e:
        print(f"Error cancelling appointment by queue number: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return success

def change_doctor(appointment_id, new_staff_id):
    """
    Reassigns an appointment to a different doctor/medical staff member.
    Returns True if successful, else False.
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
        print(f"Error while changing doctor: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return success

def put_in_queue(appointment_id):
    """
    Updates an appointment's status to 'IN_QUEUE'.
    Returns True if successful, else False.
    """
    connection = get_db_connection()
    if not connection:
        return False

    success = False
    try:
        cursor = connection.cursor()
        query = "UPDATE appointments SET status = 'IN_QUEUE' WHERE appointment_id = %s"
        cursor.execute(query, (appointment_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Appointment ID {appointment_id} is now placed in the queue ('IN_QUEUE').")
            success = True
        else:
            print(f"No appointment found with ID {appointment_id}.")

    except Error as e:
        print(f"Error while putting appointment in queue: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return success

def get_appointment_by_user_id(user_id):
    """
    Retrieves all appointments belonging to a specific user (via the patients table).
    Returns a list of dictionaries containing appointment details.
    """
    connection = get_db_connection()
    if not connection:
        return []

    appointments = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT a.* FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE p.user_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """
        cursor.execute(query, (user_id,))
        appointments = cursor.fetchall()

    except Error as e:
        print(f"Error while fetching appointments by user ID: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return appointments

def get_all_appointment_by_doctor(staff_id):
    """
    Retrieves all appointments assigned to a specific medical staff/doctor.
    Returns a list of dictionaries containing appointment details.
    """
    connection = get_db_connection()
    if not connection:
        return []

    appointments = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT a.*, p.first_name AS patient_first_name,
                   p.last_name AS patient_last_name, p.phone_number AS patient_phone,
                   p.date_of_birth AS patient_date_of_birth
            FROM appointments a
            JOIN patients p ON p.patient_id = a.patient_id
            WHERE a.staff_id = %s
            ORDER BY a.appointment_date ASC, a.appointment_time ASC, a.appointment_id ASC
        """
        cursor.execute(query, (staff_id,))
        appointments = cursor.fetchall()

    except Error as e:
        print(f"Error while fetching appointments by doctor: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return appointments

def get_all_scheduled_and_in_queue_and_in_progress_appointment():
    """
    Retrieves all appointments that are currently SCHEDULED, IN_QUEUE, or IN_PROGRESS.
    Returns a list of dictionaries containing appointment details, ordered by date and time.
    """
    connection = get_db_connection()
    if not connection:
        return []

    appointments = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT a.*, p.first_name AS patient_first_name,
                   p.last_name AS patient_last_name,
                   m.first_name AS doctor_first_name,
                   m.last_name AS doctor_last_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN medical_staff m ON a.staff_id = m.staff_id
            WHERE a.status IN ('SCHEDULED', 'IN_QUEUE', 'IN_PROGRESS')
            ORDER BY a.appointment_date ASC, a.appointment_time ASC
        """
        cursor.execute(query)
        appointments = cursor.fetchall()

    except Error as e:
        print(f"Error while fetching active appointments: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return appointments

def get_current_queue_ticket_by_patient_id(patient_id):
    """
    Retrieves the current active queue ticket or appointment (status 'IN_QUEUE' or 'IN_PROGRESS' or 'SCHEDULED') 
    for a specific patient. Returns a dictionary containing the appointment details, or None if none found.
    """
    connection = get_db_connection()
    if not connection:
        return None

    ticket = None
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
                        SELECT a.*, m.first_name AS provider_first_name,
                                     m.last_name AS provider_last_name, m.specialty AS provider_specialty
                        FROM appointments a
                        LEFT JOIN medical_staff m ON a.staff_id = m.staff_id
                        WHERE a.patient_id = %s
                            AND a.status IN ('IN_QUEUE', 'IN_PROGRESS', 'SCHEDULED')
                        ORDER BY CASE a.status
                                                 WHEN 'IN_PROGRESS' THEN 1
                                                 WHEN 'IN_QUEUE' THEN 2
                                                 ELSE 3
                                         END,
                                         a.appointment_date ASC, a.appointment_time ASC
            LIMIT 1
        """
        cursor.execute(query, (patient_id,))
        ticket = cursor.fetchone()

    except Error as e:
        print(f"Error while fetching current queue ticket by patient ID: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return ticket


def get_all_appointments_is_scheduled_by_patient_id(patient_id):
    """
    Retrieves all appointments that are currently in 'SCHEDULED' status for a specific patient.
    Returns a list of dictionaries containing appointment details, ordered chronologically.
    """
    connection = get_db_connection()
    if not connection:
        return []

    appointments = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT * FROM appointments 
            WHERE patient_id = %s 
              AND status = 'SCHEDULED'
            ORDER BY appointment_date ASC, appointment_time ASC
        """
        cursor.execute(query, (patient_id,))
        appointments = cursor.fetchall()

    except Error as e:
        print(f"Error while fetching scheduled appointments by patient ID: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return appointments

if __name__ == "__main__":
    print("Testing appointment repository module...")
    # Add manual integration or test calls here if desired.