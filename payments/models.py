# payments/models.py
from django.db import models

class Payment(models.Model):
    order_reference = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='TZS')
    pesapal_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    transaction_status = models.CharField(max_length=50, default='initiated')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_reference
