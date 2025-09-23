from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    # Rota de cadastro de usuário
    path('users/register/', views.register_user, name='user-register'),
]