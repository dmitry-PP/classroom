import os
import secrets
import string
import random
from datetime import timedelta
from django.utils import timezone

def generate_random_string(length, use_upper_case=True, use_digits=True):
    characters = ''
    if use_upper_case:
        characters += string.ascii_letters
    else:
        characters += string.ascii_lowercase
    if use_digits:
        characters += string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_verification_code(length=6):
    return generate_random_string(
        length=length,
        use_upper_case=False,
        use_digits=True
    )

def is_verification_code_expired(sent_at):
    if not sent_at:
        return True
    expiration_time = sent_at + timedelta(minutes=10)
    return timezone.now() > expiration_time


def file_upload_path(prefix, instance, filename, directory=None):
    ext = filename.split('.')[-1]
    filename = f"{prefix}_{generate_random_string(10)}.{ext}"
    return os.path.join(directory or prefix, filename)
