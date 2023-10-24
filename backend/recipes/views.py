from django.db.models import Sum
from django.conf import settings as s
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOnlyPermission
from api.serializers import (TagSerializer, IngredientSerializer,
                             RecipeSerializer, FavoriteSerializer,
                             ShoppingCartAddSerializer, RecipeEditSerializer)
from recipes.models import (Tag, Ingredient, Recipe, Favorite,
                            ShoppingCart, RecipeIngredientRelation)
from recipes.utils import add_ingredient, delete_ingredient


CONTENT_TYPE = 'text/plain'


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Теги."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def perform_create(self, serializer):
        tag = get_object_or_404(
            Ingredient,
            id=self.kwargs.get('tag_id')
        )
        serializer.save(
            tag=tag
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    search_fields = ('name',)

    def perform_create(self, serializer):
        ingredient = get_object_or_404(
            Ingredient,
            id=self.kwargs.get('ingredient_id')
        )
        serializer.save(
            ingredient=ingredient
        )


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer, RecipeEditSerializer
    permission_classes = (IsAuthorOnlyPermission,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipeEditSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Добавляем или удаляем рецепт в избранное."""
        if request.method == 'POST':
            return add_ingredient(
                FavoriteSerializer, Favorite, request, pk
            )
        if request.method == 'DELETE':
            return delete_ingredient(
                Favorite, request, pk
            )

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавляем или удаляем рецепт в корзину покупок."""
        if request.method == 'POST':
            return add_ingredient(
                ShoppingCartAddSerializer, ShoppingCart, request, pk
            )
        if request.method == 'DELETE':
            return delete_ingredient(
                ShoppingCart, request, pk
            )

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Загружаем список покупок в формате .txt"""
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
        response = FileResponse(groceries, content_type=CONTENT_TYPE)
        response['Content-Disposition'] = (
            f'attachment; filename="{s.FILENAME}"'
        )
        return response
