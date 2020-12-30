from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'user'
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>=<token>/', views.activate, name='activate'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('reset-password/', views.password_reset, name='password_reset'),
    path('reset-confirm/<uidb64>=<token>/', views.password_reset_confirm, name='password_reset_confirm')
]
