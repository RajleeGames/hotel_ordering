# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem, Driver

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # How many blank inlines to show

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin for the Order model, with an inline for OrderItem.
    """
    list_display = (
        'id',
        'user',
        'status',
        'created_at',
        'total_price',
        'phone_number',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    inlines = [OrderItemInline]

    fields = (
        'user',
        'status',
        'created_at',
        'total_price',
        'delivery_address',
        'driver_lat',
        'driver_lng',
    )
    readonly_fields = ('created_at',)

    def phone_number(self, obj):
        """
        Display the user's phone number from their profile, if it exists.
        """
        if hasattr(obj.user, 'profile'):
            return obj.user.profile.phone_number
        return ''
    phone_number.short_description = "Phone Number"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Optionally register OrderItem in the admin separately,
    if you want to manage them outside the inline as well.
    """
    pass


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """
    Manage your default deliverers (drivers) in the admin.
    """
    list_display = ('name', 'phone')
    search_fields = ('name', 'phone')
