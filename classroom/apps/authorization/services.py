from django.core.mail import send_mail
from django.conf import settings
from apps.utils import generate_random_string
from django.utils import timezone

def send_verification_email(user):
    verification_code = generate_random_string(
        length=6, 
        use_upper_case=False, 
        use_digits=True
    )
    
    user.verification_code = verification_code
    user.verification_code_sent_at = timezone.now()
    user.save()
    
    subject = 'Код верификации аккаунта'
    message = f'''
    Ваш код для верификации аккаунта: {verification_code}
    
    Код действителен в течение 10 минут.
    
    Если вы не запрашивали верификацию, проигнорируйте это письмо.
    '''
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    return verification_code