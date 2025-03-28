# reviews/urls.py
from django.urls import path
from .views import customer_reviews, manage_reviews

urlpatterns = [
    path("reviews/", customer_reviews, name="customer_reviews"),
    path("manage-reviews/", manage_reviews, name="manage_reviews"),  # staff-only
]
