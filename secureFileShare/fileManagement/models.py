from django.db import models
from users.models import User

class EncryptedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="files", default=1) 
    name = models.CharField(max_length=255)  # Name of the file
    encrypted_data = models.BinaryField()  # Encrypted file content
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp
