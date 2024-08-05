import random
import string

# Utility function to generate a 6-character verification code
def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
