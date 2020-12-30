from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .tokens import RegisterTokenGenerator
from .models import User

from django.shortcuts import HttpResponse

def send_activation_mail(user, email, current_site):
    subject = 'Activate your account'
    message = render_to_string('email_template/activation.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': RegisterTokenGenerator().make_token(user),
    })
    send_mail(subject, message, from_email=None, recipient_list=[email])

def send_reset_mail(email, current_site):
    subject = 'Reset password'

    # Checks email is registered
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = None
    
    # Will only send email if email is registered
    # This is a silent operation meaning user will not
    # be notified if an email is not sent
    if user is not None:
        message = render_to_string('email_template/reset_password.html', {
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': PasswordResetTokenGenerator().make_token(user),
        })
        send_mail(subject, message, from_email=None, recipient_list=[email]) 
