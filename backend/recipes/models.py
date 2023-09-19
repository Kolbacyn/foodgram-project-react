from django.conf import settings as s
from django.core import validators
from django.db import models

from recipes.abstract_models import AbstractModelForCartAndFavorite
from users.models import User

NOT_A_HEX_COLOR_ERROR = 'Введенное значение не является цветом в формате HEX'
MIN_COOKING_TIME_ERROR = f'Минимальное время приготовления - {s.MIN_COOKING_TIME}'
MAX_COOKING_TIME_ERROR = f'Максимальное время приготовления - {s.MAX_COOKING_TIME}'
MIN_AMOUNT_ERROR = f'Минимальное количество ингредиента - {s.MIN_INGREDIENT_AMOUNT}'
MAX_AMOUNT_ERROR = f'Максимальное количество ингредиента - {s.MAX_INGREDIENT_AMOUNT}'


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=s.MAX_LENGTH,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=s.MAX_LENGTH,
        verbose_name='Уникальный слаг',
    )
    color = models.CharField(
        max_length=s.COLOR_LENGTH,
        default="#ffffff",
        validators=(
            validators.RegexValidator(
                regex=s.COLOR_REGEX,
                message=NOT_A_HEX_COLOR_ERROR
            ),
        ),
        verbose_name='Цвет в HEX',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'slug', 'color'),
                name='unique_tag',
            ),
        )
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингидиента."""
    name = models.CharField(
        max_length=s.MAX_LENGTH,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=s.MAX_LENGTH,
        verbose_name='Единицы измерения',
        null=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
        null=True,
        blank=False,
        default=None
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги к рецепту',
        related_name='tags'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Необходимые ингредиенты',
        through='RecipeIngredientRelation',
    )
    name = models.CharField(
        max_length=s.MAX_LENGTH,
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
        default=s.MIN_COOKING_TIME,
        validators=(
            validators.MinValueValidator(
                s.MIN_COOKING_TIME,
                message=MIN_COOKING_TIME_ERROR
            ),
            validators.MaxValueValidator(
                s.MAX_COOKING_TIME,
                message=MAX_COOKING_TIME_ERROR
            ),
        ),
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

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
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'ingredients'),
                name='unique_grocery'
            ),
        )

    def __str__(self):
        return f'Ингредиенты для {self.recipe} добавлены в Ваш список покупок'


class Favorite(AbstractModelForCartAndFavorite):
    """Модель добавления рецепта в избранное."""
    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в избранном пользователя {self.user.username}'


class RecipeIngredientRelation(models.Model):
    """Модель связывающая рецепты и ингредиенты."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Связаный рецепт',
        related_name='related_recipe',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Связаный ингредиент',
        related_name='list_of_ingredients',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        default=s.MIN_INGREDIENT_AMOUNT,
        verbose_name='Количество ингредиента',
        validators=(
            validators.MinValueValidator(
                s.MIN_INGREDIENT_AMOUNT,
                message=MIN_AMOUNT_ERROR,
            ),
            validators.MaxValueValidator(
                s.MAX_INGREDIENT_AMOUNT,
                message=MAX_AMOUNT_ERROR,
            ),
        ),
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient_recipe'
            ),
        )

    def __str__(self):
        return f'{self.amount} {self.ingredient}'
