import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from views.components.card import Card
from views.components.button import Button
from views.components.text_field import TextField
from views.cancel_appointment_view import CancelAppointmentModal
from views.views.change_doctor_view import ChangeDoctorModal
from repository import appointment_repo
from service.medical_staff_service import call_next_patient, has_in_progress_appointment
from datetime import date, datetime, time

class StaffView(tk.Frame):
    def __init__(self, parent, logout_callback):
        super().__init__(parent, bg="#0B2545")
        self.logout_callback = logout_callback
        self.appointments = []
        self.selected_appointment = None
        
        self.create_header()
        self.create_main_content()
        
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
            right_frame, text="Staff Operations Control   |   ", 
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
        
        # Configure layout weights for two-column design
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        
        # --- LEFT CARD: Search & Queue Registry Table ---
        left_card = Card(container, bg="white")
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        left_inner = tk.Frame(left_card, bg="white", padx=25, pady=25)
        left_inner.pack(fill="both", expand=True)
        
        tk.Label(
            left_inner, text="QUICK PATIENT SEARCH & FILTERING", 
            font=("Arial", 9, "bold"), fg="#6B7280", bg="white", anchor="w"
        ).pack(fill="x", pady=(0, 8))
        
        search_frame = tk.Frame(left_inner, bg="white")
        search_frame.pack(fill="x", pady=(0, 20))
        
        self.search_field = TextField(search_frame)
        self.search_field.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_field.entry.insert(0, "Search by Patient ID, Name, or Assigned Doctor...")
        self.search_field.entry.config(fg="#9CA3AF")
        self.search_field.entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_field.entry.bind("<FocusOut>", self.on_search_focus_out)
        
        filter_btn = Button(search_frame, text="Filter Table", command=self.handle_filter, bg="#E5E7EB", fg="#111827")
        filter_btn.pack(side="right", ipadx=10, ipady=6)
        
        # Registry Table using ttk.Treeview
        table_frame = tk.Frame(left_inner, bg="white")
        table_frame.pack(fill="both", expand=True)
        
        columns = ("queue", "name", "doctor", "scheduled", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        self.tree.heading("queue", text="QUEUE #")
        self.tree.heading("name", text="PATIENT NAME")
        self.tree.heading("doctor", text="ASSIGNED DOCTOR")
        self.tree.heading("scheduled", text="SCHEDULED")
        self.tree.heading("status", text="STATUS")
        
        self.tree.column("queue", width=90, anchor="w")
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("doctor", width=140, anchor="w")
        self.tree.column("scheduled", width=100, anchor="w")
        self.tree.column("status", width=110, anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.handle_ticket_selection)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # --- RIGHT CARD: Queue Controls Sidebar ---
        right_card = Card(container, bg="white")
        right_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        
        right_inner = tk.Frame(right_card, bg="white", padx=25, pady=25)
        right_inner.pack(fill="both", expand=True)
        
        tk.Label(
            right_inner, text="Queue Controls", 
            font=("Arial", 14, "bold"), fg="#111827", bg="white", anchor="w"
        ).pack(fill="x", pady=(0, 4))
        
        tk.Label(
            right_inner, text="Select an active ticket from the registry to adjust status", 
            font=("Arial", 9), fg="#6B7280", bg="white", anchor="w"
        ).pack(fill="x", pady=(0, 25))
        
        self.selected_ticket_field = TextField(right_inner, label_text="SELECTED ACTIVE TICKET")
        self.selected_ticket_field.pack(fill="x", pady=(0, 25))
        
        check_in_btn = Button(right_inner, text="Check-In / Put in Queue", command=self.handle_check_in, bg="#38BDF8", fg="white")
        check_in_btn.pack(fill="x", ipady=8, pady=(0, 12))
        
        assign_btn = Button(right_inner, text="Assign/Change Doctor", command=self.handle_assign_doctor, bg="#38BDF8", fg="white")
        assign_btn.pack(fill="x", ipady=8, pady=(0, 12))
        
        cancel_btn = Button(right_inner, text="Cancel Appointment", command=self.handle_cancel, bg="#38BDF8", fg="white")
        cancel_btn.pack(fill="x", ipady=8)
        self.load_appointments()

    def on_search_focus_in(self, event):
        if self.search_field.entry.get() == "Search by Patient ID, Name, or Assigned Doctor...":
            self.search_field.entry.delete(0, tk.END)
            self.search_field.entry.config(fg="#111827")

    def on_search_focus_out(self, event):
        if not self.search_field.entry.get():
            self.search_field.entry.insert(0, "Search by Patient ID, Name, or Assigned Doctor...")
            self.search_field.entry.config(fg="#9CA3AF")

    def handle_filter(self):
        query = self.search_field.entry.get().strip()
        if query == "Search by Patient ID, Name, or Assigned Doctor...":
            query = ""
        query = query.casefold()
        matches = [
            appointment for appointment in self.appointments
            if not query or query in " ".join(str(appointment.get(field, "")) for field in (
                "appointment_id", "patient_id", "queue_number",
                "patient_first_name", "patient_last_name",
                "doctor_first_name", "doctor_last_name"
            )).casefold()
        ]
        self._render_appointments(matches)

    def load_appointments(self):
        self.appointments = appointment_repo.get_all_scheduled_and_in_queue_and_in_progress_appointment()
        self.handle_filter()

    def _render_appointments(self, appointments):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.selected_appointment = None
        self.selected_ticket_field.entry.delete(0, tk.END)

        for appointment in appointments:
            patient_name = f"{appointment.get('patient_first_name', '')} {appointment.get('patient_last_name', '')}".strip()
            doctor_name = f"Dr. {appointment.get('doctor_first_name', '')} {appointment.get('doctor_last_name', '')}".strip()
            appointment_date = appointment.get("appointment_date")
            appointment_time = appointment.get("appointment_time")
            if isinstance(appointment_date, datetime):
                appointment_date = appointment_date.date()
            if isinstance(appointment_date, date):
                scheduled_date = appointment_date.strftime("%m/%d/%y")
            else:
                scheduled_date = str(appointment_date or "")
            if isinstance(appointment_time, time):
                scheduled_time = appointment_time.strftime("%I:%M %p").lstrip("0")
            else:
                try:
                    scheduled_time = datetime.strptime(str(appointment_time), "%H:%M:%S").strftime("%I:%M %p").lstrip("0")
                except ValueError:
                    scheduled_time = str(appointment_time or "")

            self.tree.insert(
                "",
                "end",
                iid=str(appointment["appointment_id"]),
                values=(
                    appointment.get("queue_number", ""), patient_name, doctor_name,
                    f"{scheduled_date} {scheduled_time}".strip(), appointment.get("status", "")
                )
            )

    def handle_ticket_selection(self, _event=None):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        appointment_id = int(selected_items[0])
        self.selected_appointment = next(
            (appointment for appointment in self.appointments
             if appointment["appointment_id"] == appointment_id),
            None
        )
        if self.selected_appointment:
            self.selected_ticket_field.entry.delete(0, tk.END)
            self.selected_ticket_field.entry.insert(0, self.selected_appointment["queue_number"])

    def handle_check_in(self):
        appointment = self.selected_appointment
        if not appointment:
            messagebox.showerror("Select a ticket", "Select an appointment from the registry first.", parent=self)
            return
        staff_id = appointment.get("staff_id")
        if not staff_id:
            messagebox.showerror("Doctor unavailable", "The selected appointment has no assigned doctor.", parent=self)
            return

        in_progress = has_in_progress_appointment(staff_id)
        if in_progress is None:
            messagebox.showerror("Queue unavailable", "Could not check the doctor's current queue.", parent=self)
            return
        if in_progress:
            messagebox.showinfo("Doctor busy", "This doctor already has an appointment in progress.", parent=self)
            return
        if not messagebox.askyesno(
            "Call next patient",
            "No appointment is currently in progress for this doctor. Call the next patient?",
            parent=self
        ):
            return

        called_appointment = call_next_patient(staff_id)
        if not called_appointment:
            messagebox.showinfo("Queue empty", "There are no scheduled or queued appointments for this doctor.", parent=self)
            return
        self.load_appointments()
        messagebox.showinfo(
            "Patient called",
            f"Ticket {called_appointment['queue_number']} is now in progress.",
            parent=self
        )

    def handle_assign_doctor(self):
        if not self.selected_appointment:
            messagebox.showerror("Select a ticket", "Select an appointment from the registry first.", parent=self)
            return
        appointment_data = self._get_selected_appointment_view_data()
        ChangeDoctorModal(self, appointment_data, on_success=self.load_appointments)

    def handle_cancel(self):
        if not self.selected_appointment:
            messagebox.showerror("Select a ticket", "Select an appointment from the registry first.", parent=self)
            return
        appointment_data = self._get_selected_appointment_view_data()
        CancelAppointmentModal(self, appointment_data, on_success=self.load_appointments)

    def _get_selected_appointment_view_data(self):
        appointment = self.selected_appointment
        date_value = appointment.get("appointment_date")
        time_value = appointment.get("appointment_time")
        scheduled = f"{date_value} {time_value}"
        patient_name = f"{appointment.get('patient_first_name', '')} {appointment.get('patient_last_name', '')}".strip()
        doctor_name = f"Dr. {appointment.get('doctor_first_name', '')} {appointment.get('doctor_last_name', '')}".strip()
        return {
            **appointment,
            "patient_name": patient_name,
            "doctor_name": doctor_name or "Unassigned",
            "schedule": scheduled,
        }