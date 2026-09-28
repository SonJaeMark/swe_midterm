import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from repository import appointment_repo
from config.db_conn import get_db_connection
from service import patient_service

class ViewAppointmentModal(tk.Toplevel):
    def __init__(self, parent, patient_id, on_appointments_changed=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.on_appointments_changed = on_appointments_changed
        self.cancel_buttons = {}
        
        self.title("My Appointments")
        self.geometry("850x380")
        self.resizable(False, False)
        self.configure(bg="#f8f9fa")
        
        # Make modal modal-like
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_appointments()

    def create_widgets(self):
        # Header Label
        header_label = tk.Label(
            self, 
            text="MY APPOINTMENTS", 
            font=("Arial", 11, "bold"), 
            bg="#f8f9fa", 
            fg="#333333"
        )
        header_label.pack(anchor="w", padx=25, pady=(20, 5))

        # Separator line
        separator = ttk.Separator(self, orient="horizontal")
        separator.pack(fill="x", padx=25, pady=(0, 15))

        # Main Table Frame / Container
        table_frame = tk.Frame(self, bg="#ffffff", bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        # Treeview Columns
        columns = ("appointment_id", "queue", "doctor", "specialty", "scheduled", "action")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)

        # Define Column Headings & Widths
        self.tree.heading("appointment_id", text="")
        self.tree.heading("queue", text="QUEUE #")
        self.tree.heading("doctor", text="DOCTOR")
        self.tree.heading("specialty", text="SPECIALTY")
        self.tree.heading("scheduled", text="SCHEDULED")
        self.tree.heading("action", text="ACTION")

        self.tree.column("appointment_id", width=0, stretch=tk.NO) # Hidden ID column
        self.tree.column("queue", width=120, anchor="w")
        self.tree.column("doctor", width=180, anchor="w")
        self.tree.column("specialty", width=140, anchor="w")
        self.tree.column("scheduled", width=200, anchor="w")
        self.tree.column("action", width=100, anchor="center")

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self._on_tree_scroll)

        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        self.scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Configure>", lambda _event: self.after_idle(self._position_cancel_buttons))

        # Bottom Close Button Frame
        bottom_frame = tk.Frame(self, bg="#f8f9fa")
        bottom_frame.pack(fill="x", padx=25, pady=(0, 20))

        close_button = tk.Button(
            bottom_frame,
            text="Close",
            command=self.destroy,
            bg="#317873",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            bd=0,
            relief="flat",
            cursor="hand2"
        )
        close_button.pack(side="right")

    def load_appointments(self):
        """Fetches appointments from the database and populates the table."""
        for button in self.cancel_buttons.values():
            button.destroy()
        self.cancel_buttons.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)

        appointments = patient_service.view_scheduled_appointments(self.patient_id)
        
        # We also need doctor name and specialty. Let's fetch medical staff details if needed.
        connection = get_db_connection()
        staff_map = {}
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT staff_id, first_name, last_name, specialty FROM medical_staff")
                for staff in cursor.fetchall():
                    staff_map[staff['staff_id']] = staff
            except Exception as e:
                print(f"Error loading staff details: {e}")
            finally:
                connection.close()

        for appt in appointments:
            if appt['status'] == 'CANCELLED':
                continue # Skip cancelled appointments or show them differently if desired

            staff = staff_map.get(appt.get('staff_id'), {})
            doctor_name = f"DR. {staff.get('last_name', 'UNKNOWN').upper()}" if staff else "DR. UNKNOWN"
            specialty = staff.get('specialty', 'GENERAL').upper()
            
            # Format datetime
            date_str = appt['appointment_date'].strftime("%m/%d/%y")
            time_str = str(appt['appointment_time']) # Format as needed
            # Simple time formatting if stored as timedelta or time object
            try:
                from datetime import datetime
                t_obj = datetime.strptime(str(appt['appointment_time']), "%H:%M:%S")
                time_str = t_obj.strftime("%I:%M %p")
            except Exception:
                pass

            scheduled_str = f"{date_str} {time_str}"

            item_id = self.tree.insert(
                "",
                "end",
                values=(appt['appointment_id'], appt['queue_number'], doctor_name, specialty, scheduled_str, "")
            )
            self.cancel_buttons[item_id] = tk.Button(
                self.tree,
                text="Cancel",
                command=lambda appointment_id=appt['appointment_id'], queue=appt['queue_number']:
                    self.cancel_appointment(appointment_id, queue),
                bg="#B42318",
                fg="white",
                activebackground="#912018",
                activeforeground="white",
                font=("Arial", 8, "bold"),
                relief="flat",
                bd=0,
                cursor="hand2"
            )
        self.after_idle(self._position_cancel_buttons)

    def _on_tree_scroll(self, first, last):
        self.scrollbar.set(first, last)
        self.after_idle(self._position_cancel_buttons)

    def _position_cancel_buttons(self):
        for item_id, button in self.cancel_buttons.items():
            bounds = self.tree.bbox(item_id, "#6")
            if not bounds:
                button.place_forget()
                continue
            x, y, width, height = bounds
            button.place(x=x + 3, y=y + 1, width=max(1, width - 6), height=max(1, height - 2))

    def cancel_appointment(self, appointment_id, queue_number):
        confirm = messagebox.askyesno(
            "Confirm Cancellation",
            f"Are you sure you want to cancel appointment {queue_number}?",
            parent=self
        )
        if not confirm:
            return

        if appointment_repo.cancel_appointment(appointment_id):
            messagebox.showinfo("Success", f"Appointment {queue_number} has been cancelled.", parent=self)
            self.load_appointments()
            if self.on_appointments_changed:
                self.on_appointments_changed()
        else:
            messagebox.showerror("Error", "Failed to cancel the appointment. Please try again.", parent=self)

if __name__ == "__main__":
    # Test runner for standalone preview
    root = tk.Tk()
    root.withdraw()
    # Pass a test patient_id (e.g., patient ID 1)
    modal = ViewAppointmentModal(root, patient_id=1)
    root.mainloop()