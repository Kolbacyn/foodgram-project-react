from django.contrib.admin import register, display, ModelAdmin, TabularInline

from recipes.models import (Tag, Ingredient, Recipe, Favorite,
                            RecipeIngredientRelation, ShoppingCart)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    empty_value_display = '-пусто-'


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientInRecipeInline(TabularInline):
    """Определяем возможность выбора ингредиентов в рецепте."""
    model = RecipeIngredientRelation
    extra = 2
    min_num = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('author', 'name', 'count_favorites', 'recipe_tags',)
    list_filter = ('name', 'author', 'tags',)
    inlines = (IngredientInRecipeInline,)

    @display(description='Добавления в избранное')
    def count_favorites(self, obj):
        """Счетчик добавления рецепта в избранное."""
        return obj.favorites.count()

    @display(description='')
    def recipe_tags(self, obj):
        """Выводим теги к рецепту."""
        return ', '.join(_.name for _ in obj.tags.all())


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
