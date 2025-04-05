from django.urls import path
from . import views
from .views import profile_site_view

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profiles/', views.profile_view, name='profiles'),
    path('profile_site/', profile_site_view, name='profile_site'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/verify/', views.password_reset_verify, name='password_reset_verify'),
    path('password-reset/set/<str:email>/', views.password_reset_set, name='password_reset_set')
]
