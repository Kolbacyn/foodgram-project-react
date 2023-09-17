from django.urls import include, path

from rest_framework.routers import DefaultRouter

from recipes.views import (TagViewSet, IngredientViewSet, RecipeViewSet)
from users.views import CustomUserViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('rest_framework.urls')),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
