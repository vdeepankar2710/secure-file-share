from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import EncryptedFile
from django.shortcuts import get_object_or_404
from .utils.encryption import decrypt_file, derive_key
from .serializers import EncryptedFileSerializer
from .utils.encryption import encrypt_file, decrypt_file, derive_key
from .utils.secure_link import validate_secure_link, generate_secure_link

PASSWORD = "password821734"

class FileUploadView(APIView):
    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        file_data = file.read()
        key = derive_key(PASSWORD)
        encrypted_data = encrypt_file(file_data, key)

        encrypted_file = EncryptedFile.objects.create(
            name=file.name,
            encrypted_data=encrypted_data,
        )

        serializer = EncryptedFileSerializer(encrypted_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileDownloadView(APIView):
    def get(self, request, file_id):
        try:
            encrypted_file = EncryptedFile.objects.get(id=file_id)
        except EncryptedFile.DoesNotExist:
            return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        key = derive_key(PASSWORD)
        decrypted_data = decrypt_file(encrypted_file.encrypted_data, key)

        response = Response(decrypted_data, content_type="application/octet-stream")
        response["Content-Disposition"] = f"attachment; filename={encrypted_file.name}"
        return response


class SecureFileDownloadView(APIView):
    def get(self, request, file_id, expiration_time, signature):
        # Validate secure link
        if not validate_secure_link(file_id, expiration_time, signature):
            return Response({"error": "Invalid or expired link."}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve and decrypt the file
        encrypted_file = get_object_or_404(EncryptedFile, id=file_id)
        key = derive_key(PASSWORD)
        decrypted_data = decrypt_file(encrypted_file.encrypted_data, key)

        response = Response(decrypted_data, content_type="application/octet-stream")
        response["Content-Disposition"] = f"attachment; filename={encrypted_file.name}"
        return response


class GenerateSecureLinkView(APIView):
    def get(self, request, file_id):
        encrypted_file = get_object_or_404(EncryptedFile, id=file_id)
        secure_link = generate_secure_link(file_id)
        return Response({"secure_link": request.build_absolute_uri(secure_link)}, status=status.HTTP_200_OK)
