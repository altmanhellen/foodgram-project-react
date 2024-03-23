from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

api_v1_router = DefaultRouter()

api_v1_router.register(r'ingredients', IngredientViewSet,
                       basename='ingredients')
api_v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
api_v1_router.register(r'tags', TagViewSet, basename='tags')
api_v1_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(api_v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
