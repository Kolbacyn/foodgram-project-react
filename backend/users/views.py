from users.models import User
from djoser.views import UserViewSet
from api.serializers import UserSerializer, UserCreateSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated


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
