
# Create your models here.
from django.db import models
from wallet.models import Wallet

class Recipient(models.Model):
    name = models.CharField(max_length=100)
    wallet_address = models.CharField(max_length=50)
    day_added = models.DateField(auto_now_add=True)
    wallet_name = models.CharField(max_length=50, blank=True, null=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='walletRecipients', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.wallet_address})"
    class Meta:
            app_label = 'walletRecipients'