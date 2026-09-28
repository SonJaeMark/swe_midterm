import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from repository import user_repo

def login(email, password_input):
    """
    Authenticates a user by verifying their email and password.
    Returns the user dictionary if successful, or None if authentication fails.
    """
    user = user_repo.get_user_for_login(email)
    if not user:
        print(f"Login failed: User with email '{email}' not found.")
        return None

    # Note: In production, use password hashing verification (e.g., bcrypt / werkzeug).
    # Here we check against the stored password_hash field.
    if user.get('password_hash') == password_input:
        print(f"User with email '{email}' logged in successfully.")
        return user
    
    print("Login failed: Incorrect password.")
    return None

def logout(user_id):
    """
    Handles user logout logic (can be expanded for session clearing or token blacklisting).
    """
    print(f"User ID {user_id} logged out successfully.")
    return True

def update_profile(user_id, username=None, email=None, password_hash=None, role=None):
    """
    Updates general user credentials.
    Returns True if successful, else False.
    """
    return user_repo.update_user_details(
        user_id=user_id,
        username=username,
        email=email,
        password_hash=password_hash,
        role=role
    )

def get_user_info(user_id=None, username=None, email=None):
    """
    Retrieves user details by user_id or username.
    """
    return user_repo.get_user_details(user_id=user_id, username=username, email=email)