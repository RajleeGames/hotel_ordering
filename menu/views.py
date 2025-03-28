from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import FoodItem, Category, Favorite
from orders.models import Order  # Ensure your orders app has an Order model

def menu_view(request):
    # Get query parameters
    query = request.GET.get('q', '')
    selected_category = request.GET.get('category', '')
    page_number = request.GET.get('page', 1)
    
    # Retrieve all categories for filtering and dropdown
    categories = Category.objects.all()
    
    # Base queryset: available food items
    food_items = FoodItem.objects.filter(is_available=True)
    
    # Special filtering based on selected category
    if selected_category:
        if selected_category == 'for-you':
            food_items = food_items.filter(is_recommended=True)
        elif selected_category == 'favorite':
            if request.user.is_authenticated:
                fav_ids = Favorite.objects.filter(user=request.user).values_list('food_item__id', flat=True)
                food_items = food_items.filter(id__in=fav_ids)
            else:
                food_items = FoodItem.objects.none()
        else:
            # If the parameter is digits, filter by ID; otherwise by slug.
            if selected_category.isdigit():
                food_items = food_items.filter(category__id=selected_category)
            else:
                food_items = food_items.filter(category__slug=selected_category)
    
    # Apply search query if provided
    if query:
        food_items = food_items.filter(name__icontains=query)
    
    # Pagination (20 items per page)
    paginator = Paginator(food_items, 20)
    page_obj = paginator.get_page(page_number)
    
    # Determine if this is the default grouped view (when no filters are active)
    grouped = not (query or selected_category)
    
    # Retrieve the most recent order for the authenticated user (if any)
    order = None
    user_favorites = set()
    
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user).order_by('-created_at').first()
        user_favorites = set(Favorite.objects.filter(user=request.user).values_list('food_item_id', flat=True))
    
    context = {
        'categories': categories,
        'food_items': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'selected_category': selected_category,
        'grouped': grouped,
        'order': order,
        'user_favorites': user_favorites,  # Pass the favorite items
    }
    return render(request, 'menu/menu.html', context)

@login_required
def toggle_favorite(request, item_id):
    """Toggle favorite status for a food item"""
    item = get_object_or_404(FoodItem, id=item_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, food_item=item)

    if not created:
        favorite.delete()  # Remove favorite if it already exists

    return redirect(request.META.get('HTTP_REFERER', 'menu'))  # Redirect back to menu

def customer_support_view(request):
    return render(request, 'customer_support.html')
