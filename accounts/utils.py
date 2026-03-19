import random
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(100000,999999))

def send_otp_email(email,otp):
    send_mail(
        'Your OTP Verification',
        f'Your OTP is {otp}',
        'noreply@test.com',
        [email],
        fail_silently=False,
    )