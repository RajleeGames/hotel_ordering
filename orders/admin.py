from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # How many blank inlines to show

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total_price', 'phone_number')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    inlines = [OrderItemInline]

    def phone_number(self, obj):
        """
        Display the user's phone number from their profile, if it exists.
        """
        return obj.user.profile.phone_number if hasattr(obj.user, 'profile') else ''
    phone_number.short_description = "Phone Number"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Optionally register OrderItem in the admin separately,
    if you want to manage them outside the inline as well.
    """
    pass
