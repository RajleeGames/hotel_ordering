from django.contrib import admin
from .models import Category, FoodItem, Favorite

admin.site.register(Category)
admin.site.register(FoodItem)
admin.site.register(Favorite)
