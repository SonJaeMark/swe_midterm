import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service.medical_staff_service import assign_doctor, get_available_doctors

class ChangeDoctorModal(tk.Toplevel):
    def __init__(self, parent, appointment_data, on_success=None):
        super().__init__(parent)
        self.appointment_data = appointment_data  # Dictionary containing appointment details
        self.on_success = on_success  # Callback function to refresh tables/views on success
        
        self.title("Change Doctor")
        self.geometry("450x380")
        self.resizable(False, False)
        self.configure(bg="#ffffff")
        
        # Modal behavior
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        # Header Section
        header_frame = tk.Frame(self, bg="#ffffff")
        header_frame.pack(fill="x", padx=25, pady=(25, 10))
        
        title_label = tk.Label(
            header_frame, 
            text="Change Doctor", 
            font=("Arial", 14, "bold"), 
            fg="#111827", 
            bg="#ffffff"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Active ticket from the registry to be Cancelled", 
            font=("Arial", 9), 
            fg="#6B7280", 
            bg="#ffffff"
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # Main Container Fields Box
        content_frame = tk.Frame(self, bg="#ffffff", padx=25, pady=5)
        content_frame.pack(fill="x")
        
        # ACTIVE TICKET Section
        tk.Label(
            content_frame, 
            text="ACTIVE TICKET", 
            font=("Arial", 8, "bold"), 
            fg="#6B7280", 
            bg="#ffffff"
        ).pack(anchor="w")
        
        queue_num = self.appointment_data.get('queue_number', 'Q-104')
        patient_name = self.appointment_data.get('patient_name', 'John Doe')
        ticket_text = f"{queue_num} ({patient_name})"
        
        # Ticket Display Box (Styled Entry/Frame look)
        ticket_box = tk.Frame(content_frame, bg="#ffffff", bd=1, relief="solid", highlightbackground="#D1D5DB", highlightthickness=1)
        ticket_box.pack(fill="x", pady=(4, 12))
        
        tk.Label(
            ticket_box, 
            text=ticket_text, 
            font=("Arial", 11), 
            fg="#111827", 
            bg="#ffffff",
            padx=10,
            pady=8
        ).pack(anchor="w")

        # ASSIGNED DOCTOR: Dropdown/Selection Section
        tk.Label(
            content_frame, 
            text="ASSIGNED DOCTOR:", 
            font=("Arial", 8, "bold"), 
            fg="#6B7280", 
            bg="#ffffff"
        ).pack(anchor="w")
        
        self.doctors = get_available_doctors()
        self.doctor_ids_by_label = {}
        self.doctor_var = tk.StringVar()
        for doctor in self.doctors:
            doctor_name = f"Dr. {doctor['first_name']} {doctor['last_name']}"
            specialty = doctor.get("specialty")
            label = f"{doctor_name} ({specialty})" if specialty else doctor_name
            self.doctor_ids_by_label[label] = doctor["staff_id"]
        current_label = next(
            (label for label, staff_id in self.doctor_ids_by_label.items()
             if staff_id == self.appointment_data.get("staff_id")),
            "Select a doctor" if self.doctor_ids_by_label else "No doctors available"
        )
        self.doctor_var.set(current_label)
        
        # Combobox to allow changing the doctor
        self.doctor_combobox = ttk.Combobox(
            content_frame, 
            textvariable=self.doctor_var,
            values=["Select a doctor", *self.doctor_ids_by_label] if self.doctor_ids_by_label else ["No doctors available"],
            state="readonly",
            font=("Arial", 10)
        )
        self.doctor_combobox.pack(fill="x", pady=(4, 12), ipady=4)

        # Metadata Labels (Schedule & Status)
        schedule = self.appointment_data.get('schedule', '10:00AM')
        status = self.appointment_data.get('status', 'IN_QUEUE')
        
        meta_frame = tk.Frame(content_frame, bg="#ffffff")
        meta_frame.pack(fill="x", pady=(2, 10))
        
        tk.Label(
            meta_frame, 
            text=f"SCHEDULE: {schedule}", 
            font=("Arial", 8, "bold"), 
            fg="#4B5563", 
            bg="#ffffff"
        ).pack(anchor="w", pady=1)
        
        tk.Label(
            meta_frame, 
            text=f"STATUS: {status}", 
            font=("Arial", 8, "bold"), 
            fg="#4B5563", 
            bg="#ffffff"
        ).pack(anchor="w", pady=1)

        # Separator Line
        separator = tk.Frame(self, bg="#E5E7EB", height=1)
        separator.pack(fill="x", padx=25, pady=(5, 15))

        # Bottom Action Buttons Frame
        btn_frame = tk.Frame(self, bg="#ffffff")
        btn_frame.pack(fill="x", padx=25, pady=(0, 20))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        confirm_btn = tk.Button(
            btn_frame,
            text="Confirm",
            command=self.handle_confirm,
            bg="#1E293B",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            pady=8
        )
        confirm_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            bg="#3B82F6",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            pady=8
        )
        cancel_btn.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def handle_confirm(self):
        """Triggers the change doctor action in the backend and closes the modal."""
        appointment_id = self.appointment_data.get("appointment_id")
        selected_doctor = self.doctor_var.get()
        new_staff_id = self.doctor_ids_by_label.get(selected_doctor)
        
        if not appointment_id or new_staff_id is None:
            messagebox.showerror("Select a doctor", "Choose an available doctor before confirming.", parent=self)
            return
        if new_staff_id == self.appointment_data.get("staff_id"):
            messagebox.showinfo("No change", "This doctor is already assigned to the appointment.", parent=self)
            return

        if assign_doctor(appointment_id, new_staff_id):
            messagebox.showinfo("Success", f"Doctor successfully changed to {selected_doctor}.", parent=self)
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to update the assigned doctor. Please try again.", parent=self)

if __name__ == "__main__":
    # Standalone test runner
    root = tk.Tk()
    root.withdraw()
    
    sample_appointment = {
        "appointment_id": 1,
        "queue_number": "Q-104",
        "patient_name": "John Doe",
        "doctor_name": "DR. VANCE",
        "schedule": "10:00AM",
        "status": "IN_QUEUE"
    }
    
    modal = ChangeDoctorModal(root, sample_appointment)
    root.mainloop()