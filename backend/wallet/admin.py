from django.contrib import admin

# Register your models here.
from .models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'address', 'created_at')
