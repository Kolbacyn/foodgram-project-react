from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from recipes.utils import add_or_delete
from api.permissions import AuthorOrReadOnly
from api.serializers import (TagSerializer, IngredientSerializer,
                             RecipeSerializer, FavoriteSerializer,
                             ShoppingCartAddSerializer, RecipeEditSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Отображение тегов."""
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer()
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
    permission_classes = (AuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipeEditSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return add_or_delete(
            FavoriteSerializer, Favorite, request, pk
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return add_or_delete(
            ShoppingCartAddSerializer, ShoppingCart, request, pk
        )
