from django.db import models

class EncryptedFile(models.Model):
    name = models.CharField(max_length=255)  # Name of the file
    encrypted_data = models.BinaryField()  # Encrypted file content
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp
