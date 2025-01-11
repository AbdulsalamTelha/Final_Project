import random
from django.core.mail import send_mail
from django.conf import settings
from smtplib import SMTPException

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user_email, otp):
    subject = "Password Reset OTP"
    message = f"Your OTP for password reset is: {otp}"
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])
        return True
    except SMTPException as e:
        print(f"Failed to send email: {e}")
        return False
