from django.shortcuts import render
from django.core.paginator import Paginator
from .models import FoodItem, Category
from orders.models import Order  # Import the Order model from your orders app

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
    
    # Use Django's Paginator; adjust the number per page as needed (currently set to 8000)
    paginator = Paginator(food_items, 8000)
    page_obj = paginator.get_page(page_number)
    
    # Determine if this is the default (grouped) view when no filters are active
    grouped = not (query or selected_category)
    
    # Retrieve the most recent order for the authenticated user (if any)
    order = None
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    
    context = {
        'categories': categories,
        'food_items': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'selected_category': selected_category,
        'grouped': grouped,
        'order': order,  # Pass the order object to the template
    }
    return render(request, 'menu/menu.html', context)


def customer_support_view(request):
    return render(request, 'customer_support.html')
