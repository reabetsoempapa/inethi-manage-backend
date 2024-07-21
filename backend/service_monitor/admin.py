from django.contrib import admin
from .models import Service
# Register your models here.
@admin.register(Service)
class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'service_type', 'api_location')