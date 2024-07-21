from django.db import models

# Assuming User model is imported here if it's in the same app,
# otherwise, you will need to import it from the respective app
from users.models import User

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.amount} - {self.description}"
