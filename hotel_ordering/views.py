# views.py in your main project folder
from django.shortcuts import render

def intro_view(request):
    return render(request, 'intro.html')
