from django.contrib import admin

from . import models


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):

    list_display = ("mac", "name", "ip", "hardware")


admin.site.register(models.Alert)
admin.site.register(models.Mesh)
admin.site.register(models.Service)
admin.site.register(models.WlanConf)
