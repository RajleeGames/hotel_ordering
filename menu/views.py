from django.shortcuts import render
from .models import FoodItem, Category

def menu_view(request):
    # Retrieve all categories and available food items
    categories = Category.objects.all()
    food_items = FoodItem.objects.filter(is_available=True)
    
    context = {
        'categories': categories,
        'food_items': food_items,
    }
    return render(request, 'menu/menu.html', context)
