from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe, RecipeIngredientRelation


def add_ingredient(add_serializer, model, request, recipe_id):
    user = request.user
    data = {'user': user.id, 'recipe': recipe_id}
    serializer = add_serializer(data=data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )


def delete_ingredient(model, request, recipe_id):
    user = request.user
    get_object_or_404(
        model,
        user=user,
        recipe=Recipe.objects.get(id=recipe_id)
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def tags_and_ingredients_set(self, recipe, tags, ingredients):
    recipe.tags.set(tags)
    RecipeIngredientRelation.objects.bulk_create(
        [RecipeIngredientRelation(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount']
        ) for ingredient in ingredients]
    )
