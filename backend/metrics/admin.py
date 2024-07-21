from django.contrib import admin

from . import models


admin.site.register(models.UptimeMetric)
admin.site.register(models.FailuresMetric)
admin.site.register(models.DataUsageMetric)
admin.site.register(models.DataRateMetric)
admin.site.register(models.ResourcesMetric)
