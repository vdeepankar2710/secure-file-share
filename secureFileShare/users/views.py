from django.core.mail import send_mail
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.conf import settings
from .models import User


class RegisterView(APIView):
    """Register a new user."""

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        username = request.data.get("username")

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)

        user.generate_otp()
        send_mail(
            "Your OTP for Login",
            f"Your OTP is {user.otp}. It is valid for 5 minutes.",
            "noreply@yourapp.com",
            [email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)


class LoginView(APIView):
    """Authenticate user and generate JWT token."""

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate and send OTP
        user.generate_otp()
        # Use an email backend to send the OTP
        send_mail(
            "Your OTP for Login",
            f"Your OTP is {user.otp}. It is valid for 5 minutes.",
            "noreply@yourapp.com",
            [email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Logout user by invalidating the token."""
    permission_classes = [IsAuthenticated]


    def post(self, request):
        try:
            # Blacklist the token (if token blacklist is used)
            token = request.auth
            refresh_token = RefreshToken(token)
            refresh_token.blacklist()

            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """Verify OTP and issue JWT token."""

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if OTP is valid
        if user.otp != otp or now() > user.otp_expiry:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Clear OTP after successful verification
        user.otp = None
        user.otp_expiry = None
        user.save()

        # Generate JWT token
        token = jwt.encode({"user_id": user.id}, settings.SECRET_KEY, algorithm="HS256")
        return Response({"message": "Login successful.", "token": token}, status=status.HTTP_200_OK)
