from django.db import models
from django.core import validators

from users.models import User


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
        ordering = ('name',)


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        null=False,
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
