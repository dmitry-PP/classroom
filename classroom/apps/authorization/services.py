from django.core.mail import send_mail
from django.conf import settings
from apps.utils import generate_random_string
from django.utils import timezone
from .models import VerifiedCodesModel, PasswordResetCodesModel

def send_verification_email(user):
    code = generate_random_string(
        length=6, 
        use_upper_case=False, 
        use_digits=True,
    )
    
    VerifiedCodesModel.objects.filter(user=user).delete()
    
    verification_code = VerifiedCodesModel.objects.create(
        user=user,
        code=code
    )
    
    subject = 'Код верификации аккаунта'
    message = f'''
    Ваш код для верификации аккаунта: {code}
    
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
    
    return code

def send_password_reset_email(user):
    """Отправка кода для сброса пароля"""
    reset_code = generate_random_string(
        length=6, 
        use_upper_case=False, 
        use_digits=True
    )

    
    PasswordResetCodesModel.objects.filter(user=user).delete()
    
    reset_code_obj = PasswordResetCodesModel.objects.create(
        user=user,
        code=reset_code
    )
    
    subject = 'Код для сброса пароля'
    message = f'''
    Ваш код для сброса пароля: {reset_code}
    
    Код действителен в течение 10 минут.
    
    Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
    '''
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    return reset_code