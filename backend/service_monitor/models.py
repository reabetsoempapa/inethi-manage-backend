from django.db import models


# Create your models here.
class Service(models.Model):
    SERVICE_TYPES = (
        ('utility', 'utility'),
        ('entertainment', 'entertainment'),
        ('games', 'games'),
        ('education', 'education')
    )

    API_LOCATIONS = (
        ('cloud', 'cloud'),
        ('local', 'local')
    )

    url = models.URLField(max_length=100, unique=True)
    name = models.CharField(max_length=20, unique=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    api_location = models.CharField(max_length=10, choices=API_LOCATIONS)
