from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Radacct)
admin.site.register(models.Radcheck)
admin.site.register(models.Radgroupcheck)
admin.site.register(models.Radgroupreply)
admin.site.register(models.Radippool)
admin.site.register(models.Radpostauth)
admin.site.register(models.Radreply)
admin.site.register(models.Radusergroup)
