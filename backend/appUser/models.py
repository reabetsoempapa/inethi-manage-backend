from django.db import models
from wallet.models import Wallet

class AppUser(models.Model):
    keycloak_username = models.CharField(max_length=50, unique=True)
    has_wallet = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING, related_name='app_users_wallet', blank=True, null=True)

    def __str__(self):
        return self.keycloak_username
