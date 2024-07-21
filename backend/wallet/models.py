from django.db import models
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
from django.utils import timezone

load_dotenv()

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')


def encrypt_private_key(private_key):
    if not ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY is not set in environment variables.")
    fernet = Fernet(ENCRYPTION_KEY)
    encrypted_key = fernet.encrypt(private_key.encode())
    return encrypted_key.decode()


def decrypt_private_key(encrypted_key):
    fernet = Fernet(ENCRYPTION_KEY)
    decrypted_key = fernet.decrypt(encrypted_key.encode())
    return decrypted_key.decode()


class Wallet(models.Model):
    address = models.CharField(max_length=50, unique=True)
    private_key = models.CharField(max_length=250)
    created_at = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=50, default='default_name')

    def save(self, *args, **kwargs):
        if not self.pk:  # Only encrypt if it's a new object
            self.private_key = encrypt_private_key(self.private_key)
        super().save(*args, **kwargs)
