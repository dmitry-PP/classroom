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

def file_upload_path(prefix, instance, filename, directory=None):
    ext = filename.split('.')[-1]
    filename = f"{prefix}_{generate_random_string(10)}.{ext}"
    return os.path.join(directory or prefix, filename)
