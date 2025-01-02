import hashlib
import hmac
import time
import os
import string
import random

PASSWORD = "strongpassword123"
SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")  # Use a strong, random key


def generate_secure_link(file_id):
    expiration_time = int(time.time()) + 600  # 10 minutes from now
    message = f"{file_id}:{expiration_time}".encode()
    signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()
    random_str = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=10))
    
    secure_link = f"/files/download/{file_id}/{expiration_time}/{signature}/{random_str}"
    return secure_link

# Utility to validate secure links
def validate_secure_link(file_id, expiration_time, signature):
    if int(expiration_time) < int(time.time()):
        return False

    message = f"{file_id}:{expiration_time}".encode()
    expected_signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, signature)
