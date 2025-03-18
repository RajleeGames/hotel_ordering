# orders/models.py
from django.db import models
from django.contrib.auth.models import User
from menu.models import FoodItem
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('on_the_way', 'On the Way'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    delivery_address = models.TextField(blank=True, null=True)

    # Fields for real-time tracking
    driver_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    driver_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # Price locked in at time of order
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    # Optional fields: start_date, end_date, usage_limit, etc.

    def __str__(self):
        return f"{self.code} - {self.discount_amount}"


@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    """
    Update the order's total price whenever an OrderItem is created, updated, or deleted.
    """
    order = instance.order
    total = sum(item.price * item.quantity for item in order.items.all())
    order.total_price = total
    order.save()
