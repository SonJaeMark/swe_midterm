import os
import sys
import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from views.components.card import Card
from views.components.button import Button
from repository import appointment_repo
from service import visit_history_service
from service.medical_staff_service import call_next_patient, complete_consultation

class DoctorView(tk.Frame):
    def __init__(self, parent, doctor_id, logout_callback):
        super().__init__(parent, bg="#0B2545")
        self.doctor_id = doctor_id
        self.logout_callback = logout_callback
        self.current_appointment = None
        
        self.create_header()
        self.create_main_content()
        self.load_current_consultation()
        self.load_visit_history()

    def create_header(self):
        header = tk.Frame(self, bg="white", height=65)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        logo_label = tk.Label(
            header, text="MediQueue", 
            font=("Arial", 14, "bold"), fg="#0B2545", bg="white"
        )
        logo_label.pack(side="left", padx=25)
        
        right_frame = tk.Frame(header, bg="white")
        right_frame.pack(side="right", padx=25)
        
        portal_label = tk.Label(
            right_frame, text="Consultation Operations   |   Logged in: Dr. Vance (Cardiology)", 
            font=("Arial", 10), fg="#4B5563", bg="white"
        )
        portal_label.pack(side="left")
        
        logout_btn = tk.Button(
            right_frame, text="LOG OUT", command=self.logout_callback,
            font=("Arial", 9, "bold"), fg="#111827", bg="white",
            relief="solid", bd=1, padx=10, pady=2, cursor="hand2",
            activebackground="#F3F4F6"
        )
        logout_btn.pack(side="left", padx=(15, 0))

    def create_main_content(self):
        container = tk.Frame(self, bg="#0B2545")
        container.pack(fill="both", expand=True, padx=25, pady=20)
        
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)
        
        # --- LEFT COLUMN (Active Calling & Consultation Form) ---
        left_col = tk.Frame(container, bg="#0B2545")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        left_col.rowconfigure(1, weight=1)
        left_col.columnconfigure(0, weight=1)
        
        # Card 1: Currently Calling Section
        top_card = Card(left_col, bg="white")
        top_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        top_inner = tk.Frame(top_card, bg="white", padx=25, pady=20)
        top_inner.pack(fill="both", expand=True)
        
        top_header_row = tk.Frame(top_inner, bg="white")
        top_header_row.pack(fill="x", pady=(0, 4))
        
        tk.Label(
            top_header_row, text="CURRENTLY CALLING", 
            font=("Arial", 8, "bold"), fg="#6B7280", bg="white"
        ).pack(side="left")
        
        self.status_badge = tk.Label(
            top_header_row, text="NO ACTIVE CONSULTATION", 
            font=("Arial", 8, "bold"), fg="white", bg="#6B7280", padx=8, pady=2
        )
        self.status_badge.pack(side="right")
        
        self.patient_name_label = tk.Label(
            top_inner, text="No active consultation", 
            font=("Arial", 20, "bold"), fg="#111827", bg="white"
        )
        self.patient_name_label.pack(anchor="w", pady=(0, 12))
        
        info_row = tk.Frame(top_inner, bg="white")
        info_row.pack(fill="x", pady=(0, 15))
        
        self.age_gender_label = tk.Label(
            info_row, text="AGE\n-", 
            font=("Arial", 9), fg="#4B5563", bg="white", justify="left"
        )
        self.age_gender_label.pack(side="left", padx=(0, 30))
        
        self.phone_label = tk.Label(
            info_row, text="PHONE CONTACT\n-", 
            font=("Arial", 9), fg="#4B5563", bg="white", justify="left"
        )
        self.phone_label.pack(side="left", padx=(0, 30))
        
        self.queue_label = tk.Label(
            info_row, text="QUEUE NUMBER\n-", 
            font=("Arial", 9), fg="#4B5563", bg="white", justify="left"
        )
        self.queue_label.pack(side="left")
        
        call_next_btn = Button(
            top_inner, text="Call Next Patient (Advance Queue)", 
            command=self.handle_call_next, bg="white", fg="#111827"
        )
        call_next_btn.pack(fill="x", ipady=8)
        # Override border/outline style for secondary button look
        call_next_btn.config(relief="solid", bd=1, highlightbackground="#D1D5DB")

        # Card 2: Session Consultation Notes Form
        bottom_card = Card(left_col, bg="white")
        bottom_card.grid(row=1, column=0, sticky="nsew")
        
        bottom_inner = tk.Frame(bottom_card, bg="white", padx=25, pady=20)
        bottom_inner.pack(fill="both", expand=True)
        
        tk.Label(
            bottom_inner, text="Session Consultation Notes", 
            font=("Arial", 13, "bold"), fg="#111827", bg="white", anchor="w"
        ).pack(fill="x", pady=(0, 2))
        
        # Clinical Diagnosis Field
        tk.Label(
            bottom_inner, text="CLINICAL DIAGNOSIS", 
            font=("Arial", 8, "bold"), fg="#6B7280", bg="white", anchor="w"
        ).pack(fill="x", pady=(10, 4))
        
        self.diagnosis_entry = tk.Entry(
            bottom_inner, font=("Arial", 10), fg="#9CA3AF", relief="solid", bd=1
        )
        self.diagnosis_entry.pack(fill="x", ipady=8, pady=(0, 10))
        self.diagnosis_entry.insert(0, "e.g. Mild Mitral Valve Prolapse or Routine Screening")
        self.diagnosis_entry.bind("<FocusIn>", lambda e: self.on_entry_focus_in(self.diagnosis_entry, "e.g. Mild Mitral Valve Prolapse or Routine Screening"))
        self.diagnosis_entry.bind("<FocusOut>", lambda e: self.on_entry_focus_out(self.diagnosis_entry, "e.g. Mild Mitral Valve Prolapse or Routine Screening"))

        # Prescriptions & Directives Field
        tk.Label(
            bottom_inner, text="PRESCRIPTIONS & MEDICAL DIRECTIVES", 
            font=("Arial", 8, "bold"), fg="#6B7280", bg="white", anchor="w"
        ).pack(fill="x", pady=(4, 4))
        
        self.prescription_text = tk.Text(
            bottom_inner, font=("Arial", 10), fg="#9CA3AF", height=4, relief="solid", bd=1
        )
        self.prescription_text.pack(fill="x", pady=(0, 15))
        self.prescription_text.insert("1.0", "Specify dosage instructions, test logs, etc.")
        self.prescription_text.bind("<FocusIn>", lambda e: self.on_text_focus_in(self.prescription_text, "Specify dosage instructions, test logs, etc."))
        self.prescription_text.bind("<FocusOut>", lambda e: self.on_text_focus_out(self.prescription_text, "Specify dosage instructions, test logs, etc."))

        # Action Buttons
        complete_btn = Button(
            bottom_inner, text="Complete Consultation & Log Visit", 
            command=self.handle_complete_consultation, bg="#1E293B", fg="white"
        )
        complete_btn.pack(fill="x", ipady=8, pady=(0, 10))
        
        cancel_consult_btn = Button(
            bottom_inner, text="Cancel", 
            command=self.handle_cancel_consultation, bg="#1E293B", fg="white"
        )
        cancel_consult_btn.pack(fill="x", ipady=8)

        # --- RIGHT COLUMN (Historical Visits) ---
        right_col = tk.Frame(container, bg="#0B2545")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        
        history_card = Card(right_col, bg="white")
        history_card.pack(fill="both", expand=True)
        
        history_inner = tk.Frame(history_card, bg="white", padx=25, pady=25)
        history_inner.pack(fill="both", expand=True)
        
        tk.Label(
            history_inner, text="Historical Visits", 
            font=("Arial", 13, "bold"), fg="#111827", bg="white", anchor="w"
        ).pack(fill="x")
        
        tk.Label(
            history_inner, text="Past cases and diagnosed events", 
            font=("Arial", 9), fg="#6B7280", bg="white", anchor="w"
        ).pack(fill="x", pady=(0, 15))
        
        # Scrollable area or frame for historical visit items
        self.history_scroll_frame = tk.Frame(history_inner, bg="white")
        self.history_scroll_frame.pack(fill="both", expand=True)
        
        self.render_historical_visits([])

    def render_historical_visits(self, visits):
        for widget in self.history_scroll_frame.winfo_children():
            widget.destroy()

        if not visits:
            tk.Label(
                self.history_scroll_frame,
                text="No historical visits found.",
                font=("Arial", 9), fg="#6B7280", bg="white"
            ).pack(anchor="w", pady=8)
            return
            
        for visit in visits:
            visit_box = tk.Frame(self.history_scroll_frame, bg="white", bd=1, relief="solid", highlightbackground="#D1D5DB", highlightthickness=1, padx=15, pady=12)
            visit_box.pack(fill="x", pady=(0, 12))
            
            top_row = tk.Frame(visit_box, bg="white")
            top_row.pack(fill="x")
            
            tk.Label(
                top_row,
                text=f"{visit.get('patient_first_name', '')} {visit.get('patient_last_name', '')}".strip(),
                font=("Arial", 10, "bold"), fg="#111827", bg="white"
            ).pack(side="left")

            visit_date = visit.get("visit_date")
            if isinstance(visit_date, (date, datetime)):
                visit_date = visit_date.strftime("%b %d, %Y")
            tk.Label(
                top_row, text=visit_date or "", 
                font=("Arial", 9), fg="#DC2626", bg="white"
            ).pack(side="right")

            tk.Label(
                visit_box,
                text=f"QUEUE {visit.get('queue_number', '')}  |  DIAGNOSIS",
                font=("Arial", 7, "bold"), fg="#6B7280", bg="white"
            ).pack(anchor="w", pady=(8, 2))
            
            tk.Label(
                visit_box, text=visit.get("diagnosis") or "No diagnosis recorded.", 
                font=("Arial", 9), fg="#4B5563", bg="white"
            ).pack(anchor="w")

            tk.Label(
                visit_box, text="PRESCRIPTION",
                font=("Arial", 7, "bold"), fg="#6B7280", bg="white"
            ).pack(anchor="w", pady=(8, 2))
            tk.Label(
                visit_box, text=visit.get("prescription") or "No prescription recorded.",
                font=("Arial", 9), fg="#4B5563", bg="white", wraplength=300, justify="left"
            ).pack(anchor="w")

    def on_entry_focus_in(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="#111827")

    def on_entry_focus_out(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg="#9CA3AF")

    def on_text_focus_in(self, text_widget, placeholder):
        current_val = text_widget.get("1.0", "end-1c").strip()
        if current_val == placeholder:
            text_widget.delete("1.0", tk.END)
            text_widget.config(fg="#111827")

    def on_text_focus_out(self, text_widget, placeholder):
        current_val = text_widget.get("1.0", "end-1c").strip()
        if not current_val:
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg="#9CA3AF")

    def load_current_consultation(self):
        """Fetches active consultation queue for the doctor via repository."""
        appointments = appointment_repo.get_all_appointment_by_doctor(self.doctor_id)
        in_progress = [a for a in appointments if a.get('status') == 'IN_PROGRESS']
        if in_progress:
            self.current_appointment = in_progress[0]
            self.update_ui_with_appointment(self.current_appointment)
        else:
            self.current_appointment = None
            self.patient_name_label.config(text="No active consultation")
            self.age_gender_label.config(text="AGE\n-")
            self.phone_label.config(text="PHONE CONTACT\n-")
            self.queue_label.config(text="QUEUE NUMBER\n-")
            self.status_badge.config(text="NO ACTIVE CONSULTATION", bg="#6B7280")

    def update_ui_with_appointment(self, appt):
        patient_name = f"{appt.get('patient_first_name', '')} {appt.get('patient_last_name', '')}".strip()
        self.patient_name_label.config(text=patient_name or "Patient details unavailable")
        self.phone_label.config(text=f"PHONE CONTACT\n{appt.get('patient_phone') or '-'}")
        birth_date = appt.get("patient_date_of_birth")
        age_text = "-"
        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        if isinstance(birth_date, date):
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            age_text = f"{age} years"
        self.age_gender_label.config(text=f"AGE\n{age_text}")
        self.queue_label.config(text=f"QUEUE NUMBER\n{appt.get('queue_number', '-')}")
        self.status_badge.config(text=appt.get('status', 'IN_PROGRESS'), bg="#10B981")

    def load_visit_history(self):
        visits = visit_history_service.view_history_by_doctor(self.doctor_id)
        self.render_historical_visits(visits)

    def handle_call_next(self):
        if self.current_appointment:
            messagebox.showinfo(
                "Consultation in progress",
                "Complete or cancel the current consultation before calling the next patient.",
                parent=self
            )
            return
        if not messagebox.askyesno(
            "Call next patient",
            "Call the next scheduled patient in this doctor's queue?",
            parent=self
        ):
            return

        next_appt = call_next_patient(self.doctor_id)
        if next_appt:
            self.current_appointment = next_appt
            self.update_ui_with_appointment(next_appt)
            name = f"{next_appt.get('patient_first_name', '')} {next_appt.get('patient_last_name', '')}".strip()
            messagebox.showinfo("Queue Updated", f"Now calling {name or 'the next patient'} ({next_appt.get('queue_number')}).", parent=self)
        else:
            messagebox.showinfo("Queue Empty", "No waiting patients are available for this doctor.", parent=self)

    def handle_complete_consultation(self):
        diagnosis = self.diagnosis_entry.get()
        prescription = self.prescription_text.get("1.0", "end-1c")
        
        if not self.current_appointment:
            messagebox.showerror("Error", "No active consultation in progress.", parent=self)
            return
            
        if not messagebox.askyesno(
            "Complete consultation",
            "Save these notes and mark this appointment as completed?",
            parent=self
        ):
            return

        appointment_id = self.current_appointment.get("appointment_id")
        diagnosis_placeholder = "e.g. Mild Mitral Valve Prolapse or Routine Screening"
        prescription_placeholder = "Specify dosage instructions, test logs, etc."
        diagnosis = "" if diagnosis.strip() == diagnosis_placeholder else diagnosis.strip()
        prescription = "" if prescription.strip() == prescription_placeholder else prescription.strip()
        success = complete_consultation(
            appointment_id, self.doctor_id, diagnosis, prescription
        )
        
        if success:
            messagebox.showinfo("Success", "Consultation completed and visit logged successfully.", parent=self)
            self.diagnosis_entry.delete(0, tk.END)
            self.diagnosis_entry.insert(0, diagnosis_placeholder)
            self.diagnosis_entry.config(fg="#9CA3AF")
            self.prescription_text.delete("1.0", tk.END)
            self.prescription_text.insert("1.0", prescription_placeholder)
            self.prescription_text.config(fg="#9CA3AF")
            self.load_current_consultation()
            self.load_visit_history()
        else:
            messagebox.showerror("Error", "Failed to complete consultation. Please check database logs.", parent=self)

    def handle_cancel_consultation(self):
        if not self.current_appointment:
            messagebox.showerror("Error", "There is no active consultation to cancel.", parent=self)
            return
        queue_number = self.current_appointment.get("queue_number", "this appointment")
        if not messagebox.askyesno(
            "Cancel consultation",
            f"Cancel the active consultation for {queue_number}?",
            parent=self
        ):
            return

        if appointment_repo.cancel_appointment(self.current_appointment["appointment_id"]):
            messagebox.showinfo("Cancelled", f"Consultation {queue_number} has been cancelled.", parent=self)
            self.load_current_consultation()
        else:
            messagebox.showerror("Error", "Failed to cancel the consultation.", parent=self)