from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    verification_code = db.Column(db.String(6), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the user's password."""
        return check_password_hash(self.password_hash, password)

    def generate_verification_code(self):
        """Generate a random verification code."""
        self.verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def verify_code(self, code):
        """Verify the user's verification code."""
        if self.verification_code == code:
            self.is_verified = True
            self.verification_code = None
            return True
        return False
