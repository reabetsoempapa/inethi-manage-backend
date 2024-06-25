from django.db import models
from wallet.models import Wallet

class User(models.Model):
    keycloak_username = models.CharField(max_length=50, unique=True)
    has_wallet = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING, related_name='users_wallet', default=None, blank=True)
