from django.db import models
from django.core import validators

from users.models import User
from recipes.abstract_models import AbstractModelForCartAndFavorite


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Уникальный слаг',
    )
    color = models.CharField(
        max_length=7,
        default="#ffffff",
        verbose_name='Цвет в HEX',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'slug', 'color'),
                name='unique_tag',
            ),
        )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингидиента."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента',
        null=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
        null=True
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        null=True,
        blank=False,
        default=None
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги к рецепту',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='необходимые ингредиенты',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    image = models.ImageField(
        null=True,
        default=None,
        verbose_name='Картинка',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=(
            validators.MinValueValidator(
                0,
                message='Минимальное время приготовления = 0'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class ShoppingCart(AbstractModelForCartAndFavorite):
    """Модель добавления содержимого рецепта в список покупок."""
    ingredients = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        default_related_name = 'groceries'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'ingredients'],
                name='unique_grocery'
            )
        ]

    def __str__(self):
        return f'Ингредиенты для {self.recipe} добавлены в Ваш список покупок'


class Favorite(AbstractModelForCartAndFavorite):
    """Модель добавления рецепта в избранное."""
    class Meta():
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном пользователя {self.user.username}'
