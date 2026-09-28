import tkinter as tk
from views.components.text_field import TextField
from views.components.button import Button
from views.components.link_text import LinkText
from views.components.card import Card
from views.components.dropdown import Dropdown
from views.components.header import Header
from views.components.date_field import DateField
from service import patient_service

class RegisterView(tk.Frame):
    def __init__(self, parent, switch_to_login_callback):
        super().__init__(parent, bg="#0B2545")
        self.switch_to_login = switch_to_login_callback
        
        # Use the Header component
        self.header = Header(self)
        self.header.pack(fill="x", side="top")
        
        self.create_main_content()
        
    def create_main_content(self):
        container = tk.Frame(self, bg="#0B2545")
        container.pack(fill="both", expand=True)
        
        # Centered White Card Component
        card = Card(container, bg="white")
        card.place(relx=0.5, rely=0.5, anchor="center", width=580, height=580)
        
        inner_frame = tk.Frame(card, bg="white", padx=40, pady=30)
        inner_frame.pack(fill="both", expand=True)
        
        # Title & Subtitle
        title = tk.Label(
            inner_frame, text="Register New Patient Account", 
            font=("Arial", 13, "bold"), fg="#111827", bg="white", anchor="w"
        )
        title.pack(fill="x", pady=(0, 2))
        
        subtitle = tk.Label(
            inner_frame, text="Complete all patient registration fields below", 
            font=("Arial", 9), fg="#6B7280", bg="white", anchor="w"
        )
        subtitle.pack(fill="x", pady=(0, 15))
        
        # Form Fields Grid Container
        form_grid = tk.Frame(inner_frame, bg="white")
        form_grid.pack(fill="x", pady=(0, 15))
        form_grid.columnconfigure(0, weight=1)
        form_grid.columnconfigure(1, weight=1)
        
        # Row 0: First Name & Last Name
        self.first_name_field = TextField(form_grid, label_text="FIRST NAME", placeholder="First Name")
        self.first_name_field.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))
        self.first_name_field.entry.config(fg="#9CA3AF")
        
        self.last_name_field = TextField(form_grid, label_text="LAST NAME", placeholder="Last Name")
        self.last_name_field.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        self.last_name_field.entry.config(fg="#9CA3AF")
        
        # Row 1: Email Address & Phone Number
        self.email_field = TextField(form_grid, label_text="EMAIL ADDRESS", placeholder="john.doe@mail.com")
        self.email_field.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))
        self.email_field.entry.config(fg="#9CA3AF")
        
        self.phone_field = TextField(
            form_grid, 
            label_text="PHONE NUMBER", 
            placeholder="5550192834", 
            numeric_only=True
        )
        self.phone_field.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        self.phone_field.entry.config(fg="#9CA3AF")
        
        # Row 2: Date of Birth & Password
        self.dob_field = DateField(form_grid, label_text="DATE OF BIRTH", placeholder="MM/DD/YYYY")
        self.dob_field.grid(row=2, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))
        self.dob_field.entry.config(fg="#9CA3AF")
        
        self.password_field = TextField(form_grid, label_text="PASSWORD", is_password=True, placeholder="Choose Password")
        self.password_field.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        self.password_field.entry.config(fg="#9CA3AF")
        
        # Row 3: Sex Dropdown
        self.sex_dropdown = Dropdown(form_grid, label_text="SEX", values=["Select", "Male", "Female", "Other"])
        self.sex_dropdown.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Row 4: Home Address
        self.address_field = TextField(form_grid, label_text="HOME ADDRESS", placeholder="Street Address, City, State, ZIP Code")
        self.address_field.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.address_field.entry.config(fg="#9CA3AF")
        
        # Create Account Button
        create_btn = Button(inner_frame, text="Create Account", command=self.handle_register)
        create_btn.pack(fill="x", ipady=6, pady=(5, 12))
        
        # Link to Login
        login_link = LinkText(
            inner_frame, text="Have an account, go to login", 
            command=self.switch_to_login
        )
        login_link.pack()

    def handle_register(self):
        """
        Extracts form data, validates required fields against placeholders, 
        generates a username, and calls the patient service layer to register.
        """
        first_name = self.first_name_field.entry.get().strip()
        last_name = self.last_name_field.entry.get().strip()
        email = self.email_field.entry.get().strip()
        phone_number = self.phone_field.entry.get().strip()
        date_of_birth = self.dob_field.entry.get().strip()
        password = self.password_field.entry.get().strip()
        address = self.address_field.entry.get().strip()

        # Basic validation against default placeholder strings
        if not first_name or first_name == "First Name":
            print("Validation Error: First name is required.")
            return
        if not last_name or last_name == "Last Name":
            print("Validation Error: Last name is required.")
            return
        if not email or email == "john.doe@mail.com" or "@" not in email:
            print("Validation Error: A valid email address is required.")
            return
        if not password or password == "Choose Password":
            print("Validation Error: Password is required.")
            return

        # Automatically generate a unique username from the email prefix
        username = email.split('@')[0]

        # Clean optional fields if they still contain placeholder text
        phone = phone_number if phone_number != "+1 (555) 019-2834" else None
        dob = date_of_birth if date_of_birth != "MM/DD/YYYY" else None
        addr = address if address != "Street Address, City, State, ZIP Code" else None

        # Call service layer method to save user and patient profile
        user_id = patient_service.register_patient_account(
            username=username,
            email=email,
            password_hash=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone,
            date_of_birth=dob,
            address=addr
        )

        if user_id:
            print(f"Registration successful! Patient created with User ID: {user_id}")
            # Automatically redirect back to the login view upon successful registration
            if self.switch_to_login:
                self.switch_to_login()
        else:
            print("Registration failed. Email or username might already exist in the database.")