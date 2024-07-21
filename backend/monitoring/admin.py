from django.contrib import admin

from . import models


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):

    list_display = ('name', 'hardware', 'ip')


admin.site.register(models.Alert)
admin.site.register(models.Mesh)
admin.site.register(models.UnknownNode)
admin.site.register(models.ClientSession)
