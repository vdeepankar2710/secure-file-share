import time
from cryptography.fernet import Fernet
import base64
import time
import json
from secureFileShare.settings import PASSWORD


class SecureLinkGenerator:
    def __init__(self):
        self.fernet = Fernet(PASSWORD)

    def generate_secure_token(self, file_id, expiration_minutes=20):
        """Generate an encrypted token containing file_id and expiration"""
        payload = {
            'file_id': file_id,
            'exp': int(time.time()) + (expiration_minutes * 60)
        }
        
        # Convert payload to string and encode
        payload_bytes = json.dumps(payload).encode()
        
        # Encrypt the payload
        encrypted_token = self.fernet.encrypt(payload_bytes)
        
        # Convert to URL-safe string
        return base64.urlsafe_b64encode(encrypted_token).decode()

    def verify_token(self, token):
        """Decrypt and verify the token"""
        try:
            # Convert from URL-safe string back to bytes
            encrypted_token = base64.urlsafe_b64decode(token.encode())
            
            # Decrypt the token
            decrypted_bytes = self.fernet.decrypt(encrypted_token)
            
            # Parse the payload
            payload = json.loads(decrypted_bytes.decode())
            
            # Check expiration
            if payload['exp'] < time.time():
                return None, "Link has expired"
                
            return payload, None
            
        except Exception as e:
            return None, f"Invalid token: {str(e)}"
