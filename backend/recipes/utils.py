from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from recipes.models import Recipe


def add_or_delete(add_serializer, model, request, recipe_id):
    user = request.user
    data = {'user': user.id, 'recipe': recipe_id}
    serializer = add_serializer(data=data, context={'request': request})
    if request.method == 'POST':
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)
    get_object_or_404(
        model,
        user=user,
        recipe=Recipe.objects.get(id=recipe_id)
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def download():
    pass
