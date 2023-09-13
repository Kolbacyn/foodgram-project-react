from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import FileResponse

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipes.models import (Tag, Ingredient, Recipe, Favorite,
                            ShoppingCart, RecipeIngredientRelation)
from recipes.utils import add_or_delete
from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import AuthorOrReadOnly
from api.serializers import (TagSerializer, IngredientSerializer,
                             RecipeSerializer, FavoriteSerializer,
                             ShoppingCartAddSerializer, RecipeEditSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Отображение тегов."""
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

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
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter

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
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredientRelation.objects.filter(
            recipe__groceries__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        groceries = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            groceries.append(f'\n{name} - {amount}, {unit}')
        response = FileResponse(groceries, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response
