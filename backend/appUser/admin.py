from django.contrib import admin
from .models import AppUser

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ['keycloak_username', 'has_wallet', 'created_at']
