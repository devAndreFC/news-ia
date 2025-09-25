from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar router para ViewSets
router = DefaultRouter()
router.register(r'news', views.NewsViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'profiles', views.UserProfileViewSet)

urlpatterns = [
    # Rotas de autenticação
    path('users/register/', views.register_user, name='register_user'),
    path('users/login/', views.login_user, name='login_user'),
    path('users/logout/', views.logout_user, name='logout_user'),
    
    # Rotas de preferências
    path('preferences/', views.list_categories_for_preferences, name='list_preferences'),
    
    # Rotas administrativas
    path('admin/stats/', views.admin_stats, name='admin_stats'),
    
    # Incluir rotas do router
    path('', include(router.urls)),
]