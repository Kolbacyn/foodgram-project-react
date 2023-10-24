import base64

from django.core.files.base import ContentFile
from django.conf import settings as s
from django.db.transaction import atomic
from rest_framework import serializers, exceptions, status
from rest_framework.validators import UniqueTogetherValidator

from users.models import User, Follow
from recipes.models import (Tag, Ingredient, Recipe, Favorite,
                            RecipeIngredientRelation, ShoppingCart)


MIN_COOKING_TIME_ERROR = f'Минимальное время готовки - {s.MIN_COOKING_TIME}'
MAX_COOKING_TIME_ERROR = f'Максимальное время готовки - {s.MAX_COOKING_TIME}'
MIN_AMOUNT_ERROR = f'Минимальное количество - {s.MIN_INGREDIENT_AMOUNT}'
MAX_AMOUNT_ERROR = f'Максимальное количество - {s.MAX_INGREDIENT_AMOUNT}'
UNIQUE_INGREDIENT_ERROR = 'Ингредиенты в рецепте не должны повторяться.'
NO_TAG_ERROR = 'Требуется добавить теги к рецепту.'
UNIQUE_TAG_ERROR = 'Теги к рецепту должны быть уникальными.'
SELF_FOLLOW_ERROR = 'Нельзя подписаться на себя.'
EXISTING_FOLLOW_ERROR = 'Вы уже подписаны на этого автора.'


class Base64ImageField(serializers.ImageField):
    """"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe.
    Определён укороченный набор полей для некоторых эндпоинтов."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверяем подписан ли текущий пользователь на автора."""
        user = self.context.get('request').user.id
        if Follow.objects.filter(subscriber=user, author=obj).exists():
            return True
        return False


class UserCreateSerializer(UserSerializer):
    """Сериализатор создания пользователей."""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для вывода количества ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='ingredient'
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='name'
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='measurement_unit'
    )

    class Meta:
        model = RecipeIngredientRelation
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(
        read_only=True,
        many=True,
        source='related_recipe'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """проверяем наличие рецепта в избранном."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверям наличие рецепта в корзине."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.groceries.filter(recipe=obj).exists()


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Ингредиент и количество для создания рецепта."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredientRelation
        fields = ('id', 'amount')


class RecipeEditSerializer(serializers.ModelSerializer):
    """Сериализатор создания/редактирования рецептов."""
    id = serializers.PrimaryKeyRelatedField
    cooking_time = serializers.IntegerField()
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(required=True)

    class Meta(RecipeSerializer.Meta):
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        required_fileds = '__all__'

    def validate(self, value):
        """Валидация ингредиентов и времени приготовления."""
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        for item in ingredients:
            if item['id'] in ingredients_list:
                raise exceptions.ValidationError(
                    {'ingredients': UNIQUE_INGREDIENT_ERROR}
                )
            ingredients_list.append(item['id'])
            if int(item['amount']) <= 0:
                raise exceptions.ValidationError(
                    {'amount': MIN_AMOUNT_ERROR}
                )
        cooking_time = self.initial_data.get('cooking_time')
        if cooking_time < s.MIN_COOKING_TIME:
            raise exceptions.ValidationError(
                {'cooking_time': MIN_COOKING_TIME_ERROR}
            )
        return value

    @atomic
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredientRelation.objects.bulk_create(
            [RecipeIngredientRelation(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @atomic
    def create(self, validated_data):
        """Создаем рецепт"""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        """Редактируем рецепт"""
        # Обновляем картинку
        # if 'image' in validated_data:
        #    instance.image.delete(save=False)
        #    instance.image = self.fields['image'].to_internal_value(
        #        validated_data['image']
        #    )

        # Обновляем теги и ингредиенты
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.tags_and_ingredients_set(recipe=instance,
                                      tags=tags,
                                      ingredients=ingredients)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта в избранное."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное!'
            ),
        )


class ShoppingCartAddSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в корзину."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Ингредиенты для рецепта уже добавлены в вашу корзину!'
            ),
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'last_name', 'first_name')

    def validate_subscription(self, data):
        """Валидация подписок."""
        author = self.instance
        user = self.context.get('request').user.id
        if Follow.objects.filter(subscriber=user, author=author).exists():
            raise exceptions.ValidationError(
                detail=EXISTING_FOLLOW_ERROR,
                status=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise exceptions.ValidationError(
                detail=SELF_FOLLOW_ERROR,
                status=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):
        """Получаем рецепты пользователя."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Получаем количество рецептов."""
        return obj.recipes.all().count()

    def get_is_subscribed(self, obj):
        """Проверяем подписан ли текущий пользователь на автора."""
        user = self.context.get('request').user
        return Follow.objects.filter(subscriber=user, author=obj).exists()
