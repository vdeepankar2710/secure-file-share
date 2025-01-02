
from rest_framework import serializers
from .models import EncryptedFile

class EncryptedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedFile
        fields = ['id', 'name', 'uploaded_at']