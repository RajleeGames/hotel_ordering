# hotel_ordering/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('menu.urls')),        # Existing web routes
    path('orders/', include('orders.urls')),  # Existing order pages (cart, checkout, manage_orders)
    path('accounts/', include('accounts.urls')),
    
    
    
    # NEW: DRF API
    path('api/', include('orders.api_urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
