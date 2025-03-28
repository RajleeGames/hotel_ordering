from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from django.contrib.admin.views.decorators import staff_member_required
from datetime import date, timedelta

@login_required  # Only logged-in users can leave reviews
def customer_reviews(request):
    review_submitted = False
    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        if rating and comment:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    Review.objects.create(user=request.user, rating=rating, comment=comment)
                    review_submitted = True
                    messages.success(request, "Thank you for your review!")
                    # Instead of redirecting, we render the page with review_submitted True
                else:
                    messages.error(request, "Rating must be between 1 and 5.")
            except ValueError:
                messages.error(request, "Invalid rating value.")
        else:
            messages.error(request, "Please fill in all fields.")
    
    reviews = Review.objects.all().order_by("-created_at")
    return render(request, "reviews/reviews.html", {
        "reviews": reviews,
        "review_submitted": review_submitted
    })


@staff_member_required
def manage_reviews(request):
    date_filter = request.GET.get('date_filter', '')
    qs = Review.objects.all().order_by('-created_at')

    if date_filter == 'today':
        qs = qs.filter(created_at__date=date.today())
    elif date_filter == 'yesterday':
        qs = qs.filter(created_at__date=date.today() - timedelta(days=1))
    elif date_filter == 'last_7_days':
        qs = qs.filter(created_at__date__gte=date.today() - timedelta(days=7))
    elif date_filter == 'last_30_days':
        qs = qs.filter(created_at__date__gte=date.today() - timedelta(days=30))
    elif date_filter == 'last_6_months':
        qs = qs.filter(created_at__date__gte=date.today() - timedelta(days=180))

    return render(request, 'reviews/manage_reviews.html', {
        'reviews': qs,
        'date_filter': date_filter,
    })
