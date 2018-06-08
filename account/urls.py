from django.urls import path
from . import views
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.views import password_change
from django.contrib.auth.views import password_change_done
from django.contrib.auth.views import password_reset
from django.contrib.auth.views import password_reset_done
from django.contrib.auth.views import password_reset_confirm
from django.contrib.auth.views import password_reset_complete

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('users/follow/', views.user_follow, name='user_follow'),
    path('users/<str:username>/', views.user_detail, name='user_detail'),
    path('github/login/', views.github_login, name='github_login'),
    path('github/login/callback/', views.callback, name='callback'),
    path('register/', views.register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('edit/', views.edit, name='edit'),
    path('logout-then-login/', logout_then_login, name='logout_then_login'),
    path('password-change/', password_change, name='password_change'),
    path('password-change-done/', password_change_done, name='password_change_done'),
    path('password-reset/', password_reset, name='password_reset'),
    path('password-reset-done/', password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', password_reset_complete, name='password_reset_complete'),
    path('', views.dashboard, name='dashboard')
]
