from django.db import models


class User(models.Model):
    keycloak_username = models.CharField(max_length=50, unique=True)
