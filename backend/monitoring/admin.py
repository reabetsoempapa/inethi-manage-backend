from django.contrib import admin

from . import models


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):

    list_display = ('name', 'hardware', 'ip')


@admin.register(models.Service)
class NetworkDeviceAdmin(admin.ModelAdmin):

    list_display = ('name', 'url', 'service_type', 'api_location')


admin.site.register(models.Alert)
admin.site.register(models.Mesh)
admin.site.register(models.UnknownNode)
admin.site.register(models.ClientSession)
