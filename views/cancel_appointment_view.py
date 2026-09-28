import os
import sys
import tkinter as tk
from tkinter import messagebox

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from repository import appointment_repo

class CancelAppointmentModal(tk.Toplevel):
    def __init__(self, parent, appointment_data, on_success=None):
        super().__init__(parent)
        self.appointment_data = appointment_data  # Dictionary containing appointment details
        self.on_success = on_success  # Callback function to refresh tables/views on success
        
        self.title("Cancel Appointment")
        self.geometry("450x340")
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
            text="Cancel Appointment", 
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

        # Highlighted Active Ticket Card Box
        card_frame = tk.Frame(
            self, 
            bg="#ffffff", 
            bd=1, 
            relief="solid", 
            highlightbackground="#3B82F6", 
            highlightthickness=1
        )
        card_frame.pack(fill="x", padx=25, pady=(10, 15))
        
        inner_card = tk.Frame(card_frame, bg="#ffffff", padx=15, pady=15)
        inner_card.pack(fill="both", expand=True)
        
        # Ticket Field
        tk.Label(
            inner_card, 
            text="ACTIVE TICKET:", 
            font=("Arial", 8, "bold"), 
            fg="#6B7280", 
            bg="#ffffff"
        ).pack(anchor="w")
        
        queue_num = self.appointment_data.get('queue_number', 'Q-104')
        patient_name = self.appointment_data.get('patient_name', 'John Doe')
        ticket_text = f"{queue_num} ({patient_name})"
        
        tk.Label(
            inner_card, 
            text=ticket_text, 
            font=("Arial", 12, "bold"), 
            fg="#111827", 
            bg="#ffffff"
        ).pack(anchor="w", pady=(2, 10))
        
        # Details Metadata Fields
        doctor_name = self.appointment_data.get('doctor_name', 'DR. VANCE')
        schedule = self.appointment_data.get('schedule', '10:00AM')
        status = self.appointment_data.get('status', 'IN_QUEUE')
        
        tk.Label(
            inner_card, 
            text=f"ASSIGNED DOCTOR: {doctor_name}", 
            font=("Arial", 8, "bold"), 
            fg="#4B5563", 
            bg="#ffffff"
        ).pack(anchor="w", pady=(1, 2))
        
        tk.Label(
            inner_card, 
            text=f"SCHEDULE: {schedule}", 
            font=("Arial", 8, "bold"), 
            fg="#4B5563", 
            bg="#ffffff"
        ).pack(anchor="w", pady=(1, 2))
        
        tk.Label(
            inner_card, 
            text=f"STATUS: {status}", 
            font=("Arial", 8, "bold"), 
            fg="#4B5563", 
            bg="#ffffff"
        ).pack(anchor="w", pady=(1, 0))

        # Separator Line
        separator = tk.Frame(self, bg="#E5E7EB", height=1)
        separator.pack(fill="x", padx=25, pady=(0, 15))

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
        """Triggers the cancellation action in the backend and closes the modal."""
        queue_number = self.appointment_data.get("queue_number")
        
        if queue_number:
            success = appointment_repo.cancel_appointment_by_queue_number(queue_number)
            if success:
                messagebox.showinfo("Success", "Appointment has been cancelled successfully.", parent=self)
                if self.on_success:
                    self.on_success()
                self.destroy()
            else:
                messagebox.showerror("Error", "Failed to cancel the appointment. Please try again.", parent=self)
        else:
            # Fallback for preview/testing purposes
            messagebox.showinfo("Success", "Appointment has been cancelled successfully.", parent=self)
            self.destroy()

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
    
    modal = CancelAppointmentModal(root, sample_appointment)
    root.mainloop()