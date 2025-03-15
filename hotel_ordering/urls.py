from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Main menu app (homepage)
    path('', include('menu.urls')),  
    # Orders app URLs
    path('orders/', include('orders.urls')),
    # Accounts (authentication) app URLs
    path('accounts/', include('accounts.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
