from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now, timedelta


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)

    # Avoid reverse accessor conflicts with related_name
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",  # Custom related_name to avoid conflict
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",  # Custom related_name to avoid conflict
        blank=True,
    )

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        """Generate a random 6-digit OTP."""
        self.otp = f"{random.randint(100000, 999999)}"
        self.otp_expiry = now() + timedelta(minutes=5)  # OTP expires in 5 minutes
        self.save()

    def __str__(self):
        return self.email
