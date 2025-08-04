from django.core.mail import send_mail
from django.conf import settings

def send_email(subject, message, recipient_list):
    send_mail(
        subject,
        '',  # message (text_content) is empty, as we use html_message
        settings.EMAIL_HOST_USER,
        recipient_list,
        fail_silently=False,
        html_message=message,
    )
