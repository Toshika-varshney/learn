from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None):
        if not email:
            raise ValueError("email is required")
        
        user=self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user
    

class CustomUser(AbstractBaseUser):
    email=models.EmailField(unique=True)
    is_active=models.BooleanField(default=True)
    is_verified=models.BooleanField(default=False)
    is_blocked=models.BooleanField(default=False)
    login_attempts=models.IntegerField(default=0)
    block_until=models.DateTimeField(null=True,blank=True)

    objects=CustomUserManager()

    USERNAME_FIELD='email'


class EmailOTP(models.Model):
    email=models.EmailField()
    otp=models.CharField(max_length=6)
    attempts=models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now=True)
