import base64
from django.core.files.base import ContentFile
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import User, Follow
from recipes.models import (Tag, Ingredient, Recipe, Favorite,
                            RecipeIngredientRelation, ShoppingCart)


class Base64ImageField(serializers.ImageField):
    """"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
        """проверяем подписан ли текущий пользователь на автора."""
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
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Создаем пользователя."""
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class FollowSerializer(UserSerializer):
    """Сериализатор подписок."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)

    def get_recipes(self, obj):
        """Получаем рецепты пользователя."""
        return False

    def get_recipes_count(self, obj):
        """Получаем количество рецептов."""
        return False


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

    def __init__(self, *args, **kwargs):
        """Определяем возможность выбора полей."""
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        read_only=True,
        many=True,
        source='related_recipe')

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
        user = self.context.get("view").request.user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверям наличие рецепта в корзине."""
        user = self.context.get("view").request.user
        if user.is_anonymous:
            return False
        return user.groceries.filter(recipe=obj).exists()

    def __init__(self, *args, **kwargs):
        """Определяем возможность выбора полей."""
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


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
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredientRelation.objects.bulk_create(
            [RecipeIngredientRelation(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
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
                ingredient = Ingredient.objects.get(id=ingredient_id)
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

    def to_representation(self, instance):
        return RecipeSerializer(instance,
                                context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта в избранное."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
                message='hello'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe,
            fields=['id', 'name', 'image', 'cooking_time'],
            context={'request': request}
        ).data


class ShoppingCartAddSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в корзину."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='hello'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe,
            fields=['id', 'name', 'image', 'cooking_time'],
            context={'request': request}
        ).data
