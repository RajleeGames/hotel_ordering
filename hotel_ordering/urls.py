from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 

from .views import intro_view  # Import the intro view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Set intro page as the homepage
    path('', intro_view, name='intro'),

    # Keep all other app routes
    path('menu/', include('menu.urls')),        
    path('orders/', include('orders.urls')),  
    path('accounts/', include('accounts.urls')),
    path('reviews/', include('reviews.urls')),
    path('notifications/', include('notifications.urls')),


    # NEW: DRF API
    path('api/', include('orders.api_urls')), 
]



urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
