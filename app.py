import tkinter as tk
from views.login_view import LoginView
from views.register_view import RegisterView
from views.patient_dashboard_view import PatientDashboardView
from views.staff_view import StaffView
from views.doctor_view import DoctorView
from service.medical_staff_service import get_medical_staff_by_user_id
from tkinter import messagebox
from config.init_db import initialize_database

class MediQueueApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MediQueue - Authentication Portal")
        self.geometry("950x700")
        
        # Enforce window size constraints as requested
        self.minsize(800, 600)
        self.maxsize(1024, 768)
        
        self.current_view = None
        self.show_login()
        
    def clear_current_view(self):
        for widget in self.winfo_children():
            widget.destroy()
            
    def show_login(self):
        self.clear_current_view()
        self.title("login")
        self.current_view = LoginView(self, self.show_register)
        self.current_view.pack(fill="both", expand=True)
        self.current_view.on_login_success = self.show_dashboard

    def show_register(self):
        self.clear_current_view()
        self.title("registration")
        self.current_view = RegisterView(self, self.show_login)
        self.current_view.pack(fill="both", expand=True)

    def show_dashboard(self, user):
        self.clear_current_view()
        role = user.get("role")
        if role == "DOCTOR":
            doctor = get_medical_staff_by_user_id(user.get("user_id"))
            if not doctor:
                messagebox.showerror("Doctor profile unavailable", "No doctor profile is linked to this account.", parent=self)
                self.show_login()
                return
            self.title("doctor-dashboard")
            self.current_view = DoctorView(self, doctor["staff_id"], self.show_login)
        elif role == "STAFF":
            self.title("staff-dashboard")
            self.current_view = StaffView(self, self.show_login)
        else:
            self.title("patient-dashboard")
            self.current_view = PatientDashboardView(self, self.show_login, user.get("user_id"))
        self.current_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    if not initialize_database():
        messagebox.showerror(
            "Database setup failed",
            "MediQueue could not initialize its database. Start MySQL and check the database configuration."
        )
        raise SystemExit(1)

    app = MediQueueApp()
    app.mainloop()