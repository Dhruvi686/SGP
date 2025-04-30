from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15)
    is_phone_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    def generate_otp(self):
        """Generate a 6-digit OTP"""
        otp = ''.join(random.choices(string.digits, k=6))
        self.otp = otp
        self.save()
        return otp

    def verify_otp(self, otp):
        """Verify the OTP"""
        if self.otp == otp:
            self.is_phone_verified = True
            self.otp = None
            self.save()
            return True
        return False
