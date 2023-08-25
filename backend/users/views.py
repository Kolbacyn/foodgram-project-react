from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from djoser.views import UserViewSet

from users.models import User, Follow
from api.serializers import (UserSerializer, UserCreateSerializer,
                             FollowSerializer)


class CustomUserViewSet(UserViewSet):
    """Отображение кастомной модели пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer, UserCreateSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        """Выбираем сериализатор."""
        if self.request.method in ('POST', 'PUT', 'PATCH',):
            return UserCreateSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request) -> Response:
        """Подписки пользователя."""
        user = request.user
        queryset = Follow.objects.filter(subscriber=user)
        subs = [follow.author for follow in queryset]
        serializer = FollowSerializer(
            subs,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[AllowAny]
    )
    def subscribe(self, request, **kwargs):
        """Подписываем/отписываем пользователя."""
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            serializer = FollowSerializer(author,
                                          context={'request': request})
            Follow.objects.create(subscriber=user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        get_object_or_404(Follow, subscriber=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
