import tkinter as tk
from tkinter import messagebox
from views.components.card import Card
from views.components.text_field import TextField
from views.components.button import Button
from views.components.dropdown import Dropdown
from views.components.date_field import DateField
from views.view_appointment_table import ViewAppointmentModal
from service import patient_service, user_service
from datetime import date, datetime, time
from uuid import uuid4

class PatientDashboardView(tk.Frame):
    def __init__(self, parent, logout_callback, user_id):
        super().__init__(parent, bg="#0B2545")
        self.logout_callback = logout_callback
        self.user_id = user_id
        self.patient_profile = patient_service.view_profile(user_id) if user_id is not None else None
        patient_id = self.patient_profile.get("patient_id") if self.patient_profile else None
        self.queue_ticket = patient_service.track_queue(user_id, patient_id) if patient_id is not None else None
        self.available_doctors = {}
        self.available_times = {}
        self.date_refresh_after_id = None
        
        self.create_header(parent)
        self.create_main_content()
        
    def create_header(self, parent):
        header = tk.Frame(parent, bg="white", height=65)
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
            right_frame, text="Patient Dashboard   |   ", 
            font=("Arial", 10), fg="#4B5563", bg="white"
        )
        portal_label.pack(side="left")
        
        logout_btn = tk.Button(
            right_frame, text="LOG OUT", command=self.logout_callback,
            font=("Arial", 9, "bold"), fg="#111827", bg="white",
            relief="solid", bd=1, padx=10, pady=2, cursor="hand2",
            activebackground="#F3F4F6"
        )
        logout_btn.pack(side="left")
        
    def create_main_content(self):
        container = tk.Frame(self, bg="#0B2545")
        container.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Top Queue Ticket Card
        ticket_card = Card(container, bg="white")
        ticket_card.pack(fill="x", pady=(0, 20))
        
        ticket_inner = tk.Frame(ticket_card, bg="white", padx=25, pady=18)
        ticket_inner.pack(fill="both", expand=True)
        
        # Configure columns for 4 sections inside the top card
        ticket_inner.columnconfigure(0, weight=1)
        ticket_inner.columnconfigure(1, weight=2)
        ticket_inner.columnconfigure(2, weight=2)
        ticket_inner.columnconfigure(3, weight=1)
        
        # Section 1: Current Queue Ticket
        sec1 = tk.Frame(ticket_inner, bg="white")
        sec1.grid(row=0, column=0, sticky="w")
        tk.Label(sec1, text="CURRENT QUEUE TICKET", font=("Arial", 8, "bold"), fg="#6B7280", bg="white").pack(anchor="w")
        self.ticket_number_label = tk.Label(
            sec1,
            text="",
            font=("Arial", 22, "bold"), fg="#111827", bg="white"
        )
        self.ticket_number_label.pack(anchor="w")
        
        # Section 2: Assigned Provider
        sec2 = tk.Frame(ticket_inner, bg="white")
        sec2.grid(row=0, column=1, sticky="w")
        tk.Label(sec2, text="ASSIGNED PROVIDER", font=("Arial", 8, "bold"), fg="#6B7280", bg="white").pack(anchor="w")
        self.ticket_provider_label = tk.Label(sec2, text="", font=("Arial", 11, "bold"), fg="#111827", bg="white")
        self.ticket_provider_label.pack(anchor="w", pady=(4, 0))
        
        # Section 3: Estimated Time
        sec3 = tk.Frame(ticket_inner, bg="white")
        sec3.grid(row=0, column=2, sticky="w")
        tk.Label(sec3, text="APPOINTMENT TIME", font=("Arial", 8, "bold"), fg="#6B7280", bg="white").pack(anchor="w")
        self.ticket_time_label = tk.Label(sec3, text="", font=("Arial", 11, "bold"), fg="#111827", bg="white")
        self.ticket_time_label.pack(anchor="w", pady=(4, 0))
        
        # Section 4: Ticket Status Badge
        sec4 = tk.Frame(ticket_inner, bg="white")
        sec4.grid(row=0, column=3, sticky="e")
        tk.Label(sec4, text="TICKET STATUS", font=("Arial", 8, "bold"), fg="#6B7280", bg="white").pack(anchor="e")
        self.ticket_status_badge = tk.Label(
            sec4,
            text="",
            font=("Arial", 9, "bold"), fg="white",
            bg="#6B7280", padx=8, pady=3
        )
        self.ticket_status_badge.pack(anchor="e", pady=(4, 0))
        self._update_queue_ticket_card()
        
        # Bottom Two Columns Container
        bottom_container = tk.Frame(container, bg="#0B2545")
        bottom_container.pack(fill="both", expand=True)
        bottom_container.columnconfigure(0, weight=1)
        bottom_container.columnconfigure(1, weight=1)
        
        # --- LEFT CARD: Book New Appointment ---
        left_card = Card(bottom_container, bg="white")
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        left_inner = tk.Frame(left_card, bg="white", padx=25, pady=25)
        left_inner.pack(fill="both", expand=True)
        
        tk.Label(left_inner, text="Book New Appointment", font=("Arial", 13, "bold"), fg="#111827", bg="white", anchor="w").pack(fill="x")
        tk.Label(left_inner, text="Select a medical division, date, and preferred time slot", font=("Arial", 9), fg="#6B7280", bg="white", anchor="w").pack(fill="x", pady=(0, 15))
        
        self.doctor_dropdown = Dropdown(left_inner, label_text="DOCTOR / SPECIALTY", values=["Select a date first"])
        self.doctor_dropdown.pack(fill="x", pady=(0, 12))
        self.doctor_dropdown.combo.bind("<<ComboboxSelected>>", self._on_doctor_selected)
        
        date_time_frame = tk.Frame(left_inner, bg="white")
        date_time_frame.pack(fill="x", pady=(0, 20))
        date_time_frame.columnconfigure(0, weight=1)
        date_time_frame.columnconfigure(1, weight=1)
        
        self.pref_date_field = DateField(date_time_frame, label_text="PREFERRED DATE")
        self.pref_date_field.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        self.time_slot_field = Dropdown(date_time_frame, label_text="TIME SLOT", values=["Select a doctor first"])
        self.time_slot_field.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.pref_date_field.entry_var.trace_add("write", self._on_preferred_date_changed)
        
        book_btn = Button(left_inner, text="Book Appointment", command=self.handle_book)
        book_btn.pack(fill="x", ipady=6, pady=(0, 10))
        
        view_appt_btn = Button(left_inner, text="View Appointment", command=self.handle_view_appointment)
        view_appt_btn.pack(fill="x", ipady=6)
        
        # --- RIGHT CARD: My Profile Settings ---
        right_card = Card(bottom_container, bg="white")
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        right_inner = tk.Frame(right_card, bg="white", padx=25, pady=25)
        right_inner.pack(fill="both", expand=True)
        
        tk.Label(right_inner, text="My Profile Settings", font=("Arial", 13, "bold"), fg="#111827", bg="white", anchor="w").pack(fill="x")
        tk.Label(right_inner, text="Keep your direct contact details updated below", font=("Arial", 9), fg="#6B7280", bg="white", anchor="w").pack(fill="x", pady=(0, 15))
        
        profile_grid = tk.Frame(right_inner, bg="white")
        profile_grid.pack(fill="x", pady=(0, 15))
        profile_grid.columnconfigure(0, weight=1)
        profile_grid.columnconfigure(1, weight=1)
        
        self.fname_field = TextField(profile_grid, label_text="FIRST NAME")
        self.fname_field.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))
        
        self.lname_field = TextField(profile_grid, label_text="LAST NAME")
        self.lname_field.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 10))
        
        self.email_field = TextField(profile_grid, label_text="EMAIL ADDRESS")
        self.email_field.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))
        
        self.phone_field = TextField(profile_grid, label_text="PHONE")
        self.phone_field.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 10))
        
        self.address_field = TextField(profile_grid, label_text="HOME ADDRESS")
        self.address_field.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self._populate_profile_fields()
        
        update_btn = Button(right_inner, text="Update Profile", command=self.handle_update_profile)
        update_btn.pack(fill="x", ipady=6)

    def _on_preferred_date_changed(self, *_):
        if self.date_refresh_after_id is not None:
            self.after_cancel(self.date_refresh_after_id)
        self.date_refresh_after_id = self.after(250, self._refresh_date_availability)

    def _refresh_date_availability(self):
        self.date_refresh_after_id = None
        date_value = self.pref_date_field.get_value()
        if not patient_service.format_date_for_db(date_value):
            doctor_values = ["Select a valid date"]
            self.available_doctors = {}
        else:
            doctors = patient_service.get_available_doctors_for_date(date_value)
            self.available_doctors = {}
            for doctor in doctors:
                name = f"{doctor['first_name']} {doctor['last_name']}"
                specialty = doctor.get("specialty")
                label = f"{name} ({specialty})" if specialty else name
                self.available_doctors[label] = doctor
            doctor_values = list(self.available_doctors) or ["No doctors available"]

        self.doctor_dropdown.combo.configure(values=doctor_values)
        self.doctor_dropdown.combo.set(doctor_values[0])
        self.available_times = {}
        self.time_slot_field.combo.configure(values=["Select a doctor first"])
        self.time_slot_field.combo.set("Select a doctor first")

    def _on_doctor_selected(self, _event=None):
        doctor = self.available_doctors.get(self.doctor_dropdown.get_value())
        self.available_times = {}
        if doctor:
            for slot in doctor["available_slots"]:
                label = datetime.strptime(slot, "%H:%M:%S").strftime("%I:%M %p").lstrip("0")
                self.available_times[label] = slot

        time_values = list(self.available_times) or ["No times available"]
        self.time_slot_field.combo.configure(values=time_values)
        self.time_slot_field.combo.set(time_values[0])

    def handle_book(self):
        if not self.patient_profile:
            messagebox.showerror("Booking failed", "Patient profile could not be loaded.", parent=self)
            return

        appointment_date = patient_service.format_date_for_db(self.pref_date_field.get_value())
        if not appointment_date:
            messagebox.showerror("Invalid date", "Enter a valid date in MM/DD/YYYY format.", parent=self)
            return

        doctor = self.available_doctors.get(self.doctor_dropdown.get_value())
        appointment_time = self.available_times.get(self.time_slot_field.get_value())
        if not doctor or not appointment_time:
            messagebox.showerror("Select an appointment", "Choose an available doctor and time slot.", parent=self)
            return

        patient_id = self.patient_profile["patient_id"]
        scheduled_count = patient_service.count_scheduled_appointments(patient_id)
        if scheduled_count is None:
            messagebox.showerror("Booking failed", "Could not verify your scheduled appointments.", parent=self)
            return
        if scheduled_count >= 3:
            messagebox.showerror("Appointment limit", "You can have at most three scheduled appointments.", parent=self)
            return

        queue_number = f"Q-{uuid4().hex[:12].upper()}"
        appointment_id = patient_service.schedule_appointment(
            patient_id=patient_id,
            staff_id=doctor["staff_id"],
            queue_number=queue_number,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )
        if appointment_id is None:
            messagebox.showerror(
                "Booking failed",
                "That slot is no longer available or the appointment could not be saved. Refresh availability and try again.",
                parent=self
            )
            return

        self.queue_ticket = {
            "queue_number": queue_number,
            "provider_first_name": doctor["first_name"],
            "provider_last_name": doctor["last_name"],
            "provider_specialty": doctor.get("specialty"),
            "appointment_date": datetime.strptime(appointment_date, "%Y-%m-%d").date(),
            "appointment_time": datetime.strptime(appointment_time, "%H:%M:%S").time(),
            "status": "SCHEDULED",
        }
        self._update_queue_ticket_card()
        self._refresh_date_availability()
        messagebox.showinfo("Appointment booked", "Your appointment has been scheduled.", parent=self)

    def _update_queue_ticket_card(self):
        ticket = self.queue_ticket
        self.ticket_number_label.config(
            text=ticket.get("queue_number", "No active ticket") if ticket else "No active ticket"
        )

        provider = "Unassigned"
        if ticket and ticket.get("provider_first_name"):
            provider_name = f"{ticket['provider_first_name']} {ticket.get('provider_last_name', '')}".strip()
            specialty = ticket.get("provider_specialty")
            provider = f"{provider_name} ({specialty})" if specialty else provider_name
        self.ticket_provider_label.config(text=provider)

        appointment_time = "-"
        if ticket:
            appointment_date = ticket.get("appointment_date")
            scheduled_time = ticket.get("appointment_time")
            if isinstance(appointment_date, (date, datetime)):
                appointment_date = appointment_date.strftime("%b %d, %Y")
            if isinstance(scheduled_time, time):
                scheduled_time = scheduled_time.strftime("%I:%M %p").lstrip("0")
            appointment_time = " ".join(
                str(value) for value in (scheduled_time, appointment_date) if value
            )
        self.ticket_time_label.config(text=appointment_time)
        self.ticket_status_badge.config(
            text=ticket.get("status", "NO ACTIVE TICKET") if ticket else "NO ACTIVE TICKET",
            bg="#10B981" if ticket else "#6B7280"
        )

    def _populate_profile_fields(self):
        profile = self.patient_profile or {}
        fields = (
            (self.fname_field, profile.get("first_name")),
            (self.lname_field, profile.get("last_name")),
            (self.email_field, profile.get("email")),
            (self.phone_field, profile.get("phone_number")),
            (self.address_field, profile.get("address")),
        )
        for field, value in fields:
            field.entry.delete(0, tk.END)
            field.entry.insert(0, value or "")

    def handle_update_profile(self):
        if not self.patient_profile:
            messagebox.showerror("Update failed", "Patient profile could not be loaded.", parent=self)
            return

        first_name = self.fname_field.get_value().strip()
        last_name = self.lname_field.get_value().strip()
        email = self.email_field.get_value().strip()
        if not first_name or not last_name or not email:
            messagebox.showerror("Missing information", "First name, last name, and email are required.", parent=self)
            return
        if "@" not in email:
            messagebox.showerror("Invalid email", "Enter a valid email address.", parent=self)
            return

        profile_updates = {}
        for field_name, value in (
            ("first_name", first_name),
            ("last_name", last_name),
            ("phone_number", self.phone_field.get_value().strip()),
            ("address", self.address_field.get_value().strip()),
        ):
            if value != (self.patient_profile.get(field_name) or ""):
                profile_updates[field_name] = value

        email_changed = email != (self.patient_profile.get("email") or "")
        if not profile_updates and not email_changed:
            messagebox.showinfo("Profile unchanged", "There are no profile changes to save.", parent=self)
            return

        profile_saved = True
        if profile_updates:
            profile_saved = patient_service.update_profile(
                self.patient_profile["patient_id"], **profile_updates
            )
        email_saved = True
        if email_changed:
            email_saved = user_service.update_profile(self.user_id, email=email)

        self.patient_profile = patient_service.view_profile(self.user_id) or self.patient_profile
        self._populate_profile_fields()
        if profile_saved and email_saved:
            messagebox.showinfo("Profile updated", "Your profile has been updated.", parent=self)
        else:
            messagebox.showerror(
                "Update incomplete",
                "Some changes could not be saved. Verify the email is not already in use and try again.",
                parent=self
            )

    def handle_view_appointment(self):
        if not self.patient_profile:
            messagebox.showerror("Appointments unavailable", "Patient profile could not be loaded.", parent=self)
            return
        ViewAppointmentModal(
            self,
            self.patient_profile["patient_id"],
            on_appointments_changed=self._refresh_queue_ticket
        )

    def _refresh_queue_ticket(self):
        if not self.patient_profile:
            return
        self.queue_ticket = patient_service.track_queue(
            self.user_id,
            self.patient_profile["patient_id"]
        )
        self._update_queue_ticket_card()
