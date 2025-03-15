from django.contrib import admin
from .models import Order  # ✅ Import only models that exist in orders/models.py

admin.site.register(Order)  # ✅ Register only Order model
