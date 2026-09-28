# MediQueue

MediQueue is a desktop appointment and clinic queue manager built with Python, Tkinter, and MySQL. It provides separate patient, staff, and doctor workflows.

## Requirements

- Python 3.10 or later
- MySQL Server (XAMPP is supported by the default configuration)
- `mysql-connector-python` from `requirements.txt`

Tkinter is included with most Windows Python installations. If your Python installation does not include Tkinter, install a Python distribution that includes Tcl/Tk.

## Setup and Run (Windows)

1. Start the MySQL service in XAMPP or your MySQL installation.
2. Open PowerShell in the project directory and create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the Python dependency:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Start the application:

   ```powershell
   python app.py
   ```

At startup, MediQueue checks the local MySQL server and verifies the schema by running `db.sql`. If `mediqueue_db` does not exist, it creates the database and tables and loads the demo records from `dummy.sql`. Demo records are not reinserted when the database already exists.

## Database Configuration

The default configuration expects a local MySQL server at `localhost`, with username `root` and an empty password. Update both `config/db_conn.py` and `config/init_db.py` if your MySQL credentials or host differ.

## User Roles

- **Patient:** Register, book an appointment, view or cancel scheduled appointments, and update profile details.
- **Staff:** Search and filter the active appointment registry, call the next patient for a doctor, change an assigned doctor, or cancel an appointment.
- **Doctor:** Call the next patient, record consultation diagnosis and prescription, complete or cancel a consultation, and view visit history.

## Demo Accounts

The following accounts are inserted only during a fresh database initialization. The current demo implementation compares passwords as plain text; these credentials are for local development only.

| Role | Username | Email | Password |
|---|---|---|---|
| Patient | `patient1` | `patient1@email.com` | `pass1234` |
| Staff | `staff1` | `staff1@email.com` | `pass1234` |
| Doctor | `doctor1` | `doctor1@email.com` | `pass1234` |

Additional sample staff, doctors, and a patient are defined in `dummy.sql`.

## Project Layout

- `app.py` - application startup and role-based navigation
- `config/` - MySQL connection and database initialization
- `repository/` - SQL data access
- `service/` - application workflows
- `views/` - Tkinter screens and reusable components
- `db.sql` - database schema
- `dummy.sql` - initial demo records
- `requirements.txt` - Python package dependencies
