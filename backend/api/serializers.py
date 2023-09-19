import base64

from django.core.files.base import ContentFile
from django.conf import settings as s
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions, status
from rest_framework.validators import UniqueTogetherValidator

from users.models import User, Follow
from recipes.utils import tags_and_ingredients_set
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
        user = self.context.get('request').user
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
    """ Сериализатор для вывода количество ингредиентов в рецепте."""

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
    id = serializers.IntegerField()

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

    @atomic
    def create(self, validated_data):
        """Создаем рецепт"""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        """Редактируем рецепт"""
        # Обновляем картинку
        if 'image' in validated_data:
            instance.image.delete(save=False)
            instance.image = self.fields['image'].to_internal_value(
                validated_data['image']
            )

        # Обновляем теги
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            tags = Tag.objects.filter(id__in=tags_data)
            instance.tags.set(tags)

        # Обновляем ингредиенты
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            recipe_ingredients = []
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.pop('id')
                amount = ingredient_data.pop('amount')
                ingredient = get_object_or_404(
                    Ingredient,
                    id=ingredient_id
                )
                recipe_ingredients.append(
                    RecipeIngredientRelation(
                        recipe=instance, ingredient=ingredient, amount=amount
                    )
                )
            RecipeIngredientRelation.objects.filter(recipe=instance).delete()
            RecipeIngredientRelation.objects.bulk_create(recipe_ingredients)

        # Обновляем рецепт
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance

    def validate_ingredients(self, data):
        """Валидация ингредиентов в рецепте."""
        ingredients = self.initial_data.get('ingredients')
        list_of_ingredients = []
        for item in ingredients:
            amount = item['amount']
            if int(amount) < s.MIN_INGREDIENT_AMOUNT:
                raise exceptions.ValidationError(
                    {'amount': MIN_AMOUNT_ERROR}
                )
            if int(amount) > s.MAX_INGREDIENT_AMOUN:
                raise exceptions.ValidationError(
                    {'amount': MAX_AMOUNT_ERROR}
                )
            if item['id'] in list_of_ingredients:
                raise exceptions.ValidationError(
                    {'ingredient': UNIQUE_INGREDIENT_ERROR}
                )
            list_of_ingredients.append(item['id'])
        return data

    def validate_cooking_time(self, data):
        """Проверяем время приготовления рецепта."""
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < s.MIN_COOKING_TIME:
            raise exceptions.ValidationError(
                {'cooking_time': MIN_COOKING_TIME_ERROR}
            )
        if int(cooking_time) > s.MAX_COOKING_TIME:
            raise exceptions.ValidationError(
                {'cooking_time': MAX_COOKING_TIME_ERROR}
            )
        return data

    def validate_tags(self, data):
        """Проверяем на наличие уникального тега."""
        tags = self.initial_data.get('tags')
        if not tags:
            raise exceptions.ValidationError(
                {'tags': NO_TAG_ERROR}
            )
        list_of_tags = []
        for tag in tags:
            if tag['id'] in list_of_tags:
                raise exceptions.ValidationError(
                    {'tags': UNIQUE_TAG_ERROR}
                )
            list_of_tags.append(tag['id'])
        return data


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
        user = self.context.get('request').user
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
