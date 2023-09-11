from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from djoser.views import UserViewSet

from users.models import User, Follow
from api.pagination import LimitPageNumberPagination
from api.serializers import (UserSerializer, UserCreateSerializer,
                             FollowSerializer)


class CustomUserViewSet(UserViewSet):
    """Отображение кастомной модели пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer, UserCreateSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        """Выбираем сериализатор."""
        pass
        if self.request.method in ('POST','PUT', 'PATCH',):
            return UserCreateSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Подписки пользователя."""
        return self.get_paginated_response(
            FollowSerializer(
                self.paginate_queryset(
                    User.objects.filter(followed__subscriber=request.user)
                ),
                many=True,
                context={'request': request},
            ).data
        )
    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[AllowAny]
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['id'])

        if request.method == 'POST':
            serializer = FollowSerializer(
                author, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(subscriber=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(Follow, subscriber=request.user,
                              author=author).delete()
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)

