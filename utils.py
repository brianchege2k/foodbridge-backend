import random
import string
from flask_mail import Message
from extensions import mail  # Corrected import statement

def generate_verification_code(length=6):
    """Generate a random verification code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def send_verification_email(to, code):
    """Send a verification email."""
    msg = Message('Verify your email', recipients=[to])
    msg.body = f'Your verification code is: {code}'
    mail.send(msg)
