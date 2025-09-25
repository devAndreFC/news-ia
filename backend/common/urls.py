from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar router para ViewSets
router = DefaultRouter()
router.register(r'news', views.NewsViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'profiles', views.UserProfileViewSet)

urlpatterns = [
    # URL de teste completamente nova
    path('hello/', views.test_simple_view, name='hello_test'),
    # URL de teste simples
    path('simple-test/', views.test_simple_view, name='simple_test'),
    # URL de teste
    path('test-category-suggestion/<int:news_id>/', views.test_simple_view, name='test_category_suggestions'),
    
    # Classificação de categorias (DEVE vir antes de qualquer outra rota de news)
    path('news/<int:news_id>/category-suggestion/', views.get_category_suggestions, name='get_category_suggestions'),
    path('news/classify-categories/', views.classify_news_categories, name='classify_news_categories'),
    path('news/analyze/', views.analyze_news, name='analyze_news'),
    path('news/upload-json/', views.upload_news_json, name='upload_news_json'),
    
    # Rotas de autenticação
    path('users/register/', views.register_user, name='register_user'),
    path('users/login/', views.login_user, name='login_user'),
    path('users/logout/', views.logout_user, name='logout_user'),
    
    # Rotas de preferências
    path('preferences/', views.list_categories_for_preferences, name='list_preferences'),
    
    # Rotas administrativas
    path('admin/stats/', views.admin_stats, name='admin_stats'),
    
    # Incluir rotas do router (deve vir por último)
    path('', include(router.urls)),
]