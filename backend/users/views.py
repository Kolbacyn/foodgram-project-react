from django.shortcuts import render

# Create your views here.
from users.models import User
from djoser.views import UserViewSet
from api.serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated


class CustomUserViewSet(UserViewSet):
    """Отображение кастомной модели пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
