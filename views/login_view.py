import tkinter as tk
from tkinter import messagebox
from views.components.text_field import TextField
from views.components.button import Button
from views.components.link_text import LinkText
from views.components.card import Card
from views.components.header import Header
from service import user_service

class LoginView(tk.Frame):
    def __init__(self, parent, switch_to_register_callback):
        super().__init__(parent, bg="#0B2545")
        self.switch_to_register = switch_to_register_callback
        
        # Use the Header component
        self.header = Header(self)
        self.header.pack(fill="x", side="top")
        
        self.create_main_content()
        
    def create_main_content(self):
        container = tk.Frame(self, bg="#0B2545")
        container.pack(fill="both", expand=True)
        
        card = Card(container, bg="white")
        card.place(relx=0.5, rely=0.5, anchor="center", width=500, height=480)
        
        inner_frame = tk.Frame(card, bg="white", padx=45, pady=40)
        inner_frame.pack(fill="both", expand=True)
        
        title = tk.Label(
            inner_frame, text="Access Account", 
            font=("Arial", 14, "bold"), fg="#111827", bg="white", anchor="w"
        )
        title.pack(fill="x", pady=(0, 25))
        
        self.email_field = TextField(inner_frame, label_text="EMAIL ADDRESS", placeholder="e.g. john.doe@mail.com")
        self.email_field.pack(fill="x", pady=(16, 15))
        self.email_field.entry.config(fg="#9CA3AF")
        
        self.password_field = TextField(inner_frame, label_text="PASSWORD", is_password=True, placeholder="Password")
        self.password_field.pack(fill="x", pady=(0, 25))
        
        login_btn = Button(inner_frame, text="Login", command=self.handle_login)
        login_btn.pack(fill="x", ipady=8, pady=(0, 20))
        
        links_frame = tk.Frame(inner_frame, bg="white")
        links_frame.pack(fill="x")
        
        forgot_link = LinkText(
            links_frame, text="Forgot password? Click to reset", 
            command=lambda: print("Reset password")
        )
        forgot_link.pack(pady=3)
        
        signup_link = LinkText(
            links_frame, text="Sign up an account", 
            command=self.switch_to_register
        )
        signup_link.pack(pady=3)

    def handle_login(self):
        """
        Extracts credentials from form fields, calls the user service to 
        authenticate, and triggers navigation or displays errors.
        """
        identifier = self.email_field.entry.get().strip()
        password = self.password_field.entry.get().strip()
        
        # Basic validation against placeholders and empty inputs
        if not identifier or identifier == "e.g. john.doe@mail.com":
            messagebox.showerror("Login failed", "Enter your email address or username.", parent=self)
            return
            
        if not password:
            messagebox.showerror("Login failed", "Enter your password.", parent=self)
            return
            
        # Authenticate using the service layer (following layered architecture)
        user = user_service.login(identifier, password)
        
        if user:
            messagebox.showinfo(
                "Login successful",
                f"Welcome back, {user.get('username')}.",
                parent=self
            )
            # Trigger success callback or router transition if defined
            if hasattr(self, 'on_login_success'):
                self.on_login_success(user)
            elif hasattr(self.master, 'show_dashboard'):
                self.master.show_dashboard()
        else:
            messagebox.showerror(
                "Login failed",
                "The email/username or password is incorrect.",
                parent=self
            )