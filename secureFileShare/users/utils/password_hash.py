import hashlib
import base64
import os

class PasswordHasher:
    @staticmethod
    def generate_salt():
        return base64.b64encode(os.urandom(16)).decode('utf-8')

    @staticmethod
    def hash_password(password, salt=None):
        """
        Creates a secure hash using PBKDF2 with SHA256
        Returns tuple of (hash, salt)
        """
        if not salt:
            salt = PasswordHasher.generate_salt()
        
        # Create key
        key = hashlib.pbkdf2_hmac(
            'sha256',  # Hash algorithm
            password.encode('utf-8'),  # Convert password to bytes
            salt.encode('utf-8'),  # Convert salt to bytes
            100000,  # Number of iterations (recommended by NIST)
            dklen=32  # Length of the key
        )
        
        # Convert binary hash to base64 string
        hash_str = base64.b64encode(key).decode('utf-8')
        
        return f"{salt}${hash_str}"

    @staticmethod
    def verify_password(password, stored_hash):
        """
        Verifies a password against a stored hash
        """
        try:
            salt, hash_str = stored_hash.split('$')
            new_hash = PasswordHasher.hash_password(password, salt)
            return new_hash == stored_hash
        except:
            return False
