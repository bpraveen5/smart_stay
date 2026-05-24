import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify
from .models import Hotel


def generateRandomToken():
    return str(uuid.uuid4())

def sendEmailToken(email, token):
    
    # Implement your email sending logic here
    subject = "Verify Your Email address"
    message = f"""Please  verify your email account by clicking the link below
    
    http://127.0.0.1:8000/account/verify-account/{token}
    
    """
    
    result =send_mail(
        subject,
        message,
         settings.EMAIL_HOST_USER,
         [email],
         fail_silently=False,
    )
    return result


def sendOTPtoEmail(email, otp):
    
    # Implement your email sending logic here
    subject = "otp for account login"
    message = f""" Hi, Use this OTP to login: {otp}. Please do not share this OTP with anyone.
        
    """
    
    send_mail(
        subject,
        message,
         settings.EMAIL_HOST_USER,
         [email],
         fail_silently=False,
    )
    
def generateSlug(hotel_name):
    slug = slugify(hotel_name) + "-" + str(uuid.uuid4()).split('-')[0]
    if Hotel.objects.filter(hotel_slug = slug).exists():
        return generateSlug(hotel_name)
    return slug