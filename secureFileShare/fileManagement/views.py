from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http import HttpResponse
from .models import EncryptedFile
from .serializers import EncryptedFileSerializer
from .utils.encryption import encrypt_file, decrypt_file, derive_key
import time
from secureFileShare.settings import PASSWORD
from .utils.secure_link import SecureLinkGenerator 
  

class FileUploadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
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
            user=request.user,
        )

        serializer = EncryptedFileSerializer(encrypted_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileDownloadView(APIView):
    """
        This view for downloading the requested file for file_id
    """
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
    
  
class GenerateSecureLinkView(APIView):
    """Generate secure download link for a file"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        try:
            # Check if user has permission to access this file
            encrypted_file = get_object_or_404(
                EncryptedFile, 
                id=file_id,
                user=request.user
            )
            
            # Generate secure token
            link_generator = SecureLinkGenerator()
            token = link_generator.generate_secure_token(file_id)
            
            # Create secure download URL
            secure_link = f"{request.scheme}://{request.get_host()}/file/download/{token}/"
            
            # Calculate expiration time for response
            expiration_time = time.time() + (20 * 60)  # 20 minutes from now
            
            return Response({
                "secure_link": secure_link,
                "expires_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiration_time))
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": "Failed to generate secure link",
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class SecureFileDownloadView(APIView):
    """Handle secure file downloads"""
    authentication_classes = []  # No authentication required for download
    permission_classes = []

    def get(self, request, token):
        # Verify token
        link_generator = SecureLinkGenerator()
        payload, error = link_generator.verify_token(token)
        
        if error:
            return Response({
                "error": error
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get file
            encrypted_file = get_object_or_404(EncryptedFile, id=payload['file_id'])
            
            # Prepare file response
            
            key = derive_key(PASSWORD)
            decrypted_data = decrypt_file(encrypted_file.encrypted_data, key)
            # print("decrypted_data", decrypted_data)
            
            
            # Create response with decrypted data
            response = HttpResponse(
                decrypted_data,
                content_type="application/octet-stream"
            )
            response['Content-Disposition'] = f'attachment; filename="{encrypted_file.name}"'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
            
        except Exception as e:
            return Response({
                "error": "Failed to download file",
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
 

class UserFileListView(APIView):
    """
        This view is for listing the files uploaded by a particular user
    """

    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]
    def get(self, request):
        files = EncryptedFile.objects.filter(user=request.user).order_by("-uploaded_at")
        serializer = EncryptedFileSerializer(files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)