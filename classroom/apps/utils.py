import os
import secrets
import string


def generate_random_string(length, use_upper_case=True):
    characters = string.ascii_letters if use_upper_case else string.ascii_lowercase
    characters += string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def file_upload_path(prefix, instance, filename, directory=None):
    ext = filename.split('.')[-1]
    filename = f"{prefix}_{generate_random_string(10)}.{ext}"
    return os.path.join(directory or prefix, filename)
