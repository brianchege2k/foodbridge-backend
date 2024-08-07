import random
import string

def generate_verification_code(length=6):
    """Generate a random verification code."""
    return ''.join(random.choices(string.digits, k=length))  # Generate random digits

def send_verification_email(email, code):
    """Placeholder function to send a verification email."""
    # Here you would implement the email sending logic using Flask-Mail or another email service.
    print(f'Sending verification email to {email} with code {code}')
