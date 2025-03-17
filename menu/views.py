from django.shortcuts import render
from django.core.paginator import Paginator
from .models import FoodItem, Category

def menu_view(request):
    # Get search query and category filter from GET parameters
    query = request.GET.get('q', '')
    selected_category = request.GET.get('category', '')
    page_number = request.GET.get('page', 1)
    
    # Retrieve all categories for the filter dropdown
    categories = Category.objects.all()
    
    # Base queryset: all available food items
    food_items = FoodItem.objects.filter(is_available=True)
    
    # Apply filters if provided
    if query:
        food_items = food_items.filter(name__icontains=query)
    if selected_category:
        food_items = food_items.filter(category__id=selected_category)
    
    # Use Django's Paginator: e.g., 8 items per page
    paginator = Paginator(food_items, 8000)
    page_obj = paginator.get_page(page_number)
    
    # If no filters are applied, we consider it the "grouped" (default) view
    grouped = not (query or selected_category)
    
    context = {
        'categories': categories,
        'food_items': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'selected_category': selected_category,
        'grouped': grouped,
    }
    return render(request, 'menu/menu.html', context)
