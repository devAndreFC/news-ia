"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

def api_root(request):
    """Lista todos os endpoints disponíveis na API"""
    endpoints = {
        'documentation': {
            'swagger': '/swagger/',
            'redoc': '/redoc/',
            'schema': '/api/schema/',
        },
        'auth': {
            'token': '/auth/token/',
            'token_refresh': '/auth/token/refresh/',
        },
        'news': {
            'list': '/api/news/',
            'detail': '/api/news/{id}/',
        },
        'categories': {
            'list': '/api/categories/',
        },
        'users': {
            'register': '/api/users/',
            'login': '/auth/token/',
            'profile': '/api/users/me/',
            'preferences': '/api/users/me/preferences/',
        }
    }
    return JsonResponse(endpoints)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Swagger/OpenAPI URLs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # API URLs
    path('api/', api_root, name='api-root'),
    path('api/', include('common.urls')),
    # Authentication URLs
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
