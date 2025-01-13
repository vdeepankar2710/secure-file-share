from django.utils.timezone import now 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .models import User
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from .utils.password_hash import PasswordHasher

class RegisterView(APIView):
    """Register a new user."""
    
    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")
        role = request.data.get("role", "GUEST")

        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Hash password with custom implementation
            hashed_password = PasswordHasher.hash_password(password)
            
            # Create user with hashed password
            user = User.objects.create(
                username=username,
                email=email,
                password=hashed_password,  # Store custom hash
                role=role
            )
            
        except Exception as e:
            return Response(
                {"message": "Failed creating user"}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            user.generate_otp()
            send_mail(
                "Your OTP for Login",
                f"Your OTP is {user.otp}. It is valid for 5 minutes.",
                "noreply@yourapp.com",
                [email],
                fail_silently=False,
            )
        except:
            return Response(
                {"message": "Failed sending OTP"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": "OTP sent to your email."}, 
            status=status.HTTP_200_OK
        )

class LoginView(APIView):
    """Authenticate user and generate JWT token."""
    
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role", "GUEST")

        try:
            user = User.objects.get(email=email, role=role)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or role."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Verify password using custom implementation
        if not PasswordHasher.verify_password(password, user.password):
            return Response(
                {"error": "Invalid password."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            user.generate_otp()
            send_mail(
                "Your OTP for Login",
                f"Your OTP is {user.otp}. It is valid for 5 minutes.",
                "noreply@yourapp.com",
                [email],
                fail_silently=False,
            )
        except:
            return Response(
                {"message": "Failed sending OTP"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": "OTP sent to your email."}, 
            status=status.HTTP_200_OK
        )

class LogoutView(APIView):
    """Logout user by invalidating the token."""
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
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"message": "Login successful.", "token": token.key}, status=status.HTTP_200_OK)
