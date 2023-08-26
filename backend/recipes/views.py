from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipes.models import Tag, Ingredient, Recipe
from api.serializers import (TagSerializer, IngredientSerializer,
                             RecipeSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Отображение тегов."""
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        tag = get_object_or_404(
            Ingredient,
            id=self.kwargs.get('tag_id')
        )
        serializer.save(
            author=self.request.user.is_superuser,
            tag=tag
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты."""
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, IsAuthenticated,)

    def perform_create(self, serializer):
        ingredient = get_object_or_404(
            Ingredient,
            id=self.kwargs.get('ingredient_id')
        )
        serializer.save(
            author=self.request.user.is_superuser,
            ingredient=ingredient
        )


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
