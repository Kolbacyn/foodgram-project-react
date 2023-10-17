from django.contrib.auth.models import AbstractUser
from django.conf import settings as s
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    email = models.CharField(
        verbose_name='Адрес электронной почты',
        max_length=s.MAX_EMAIL_LENGTH,
        blank=False,
        null=False,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Уникальное имя пользователя',
        max_length=s.MAX_LENGHT_FOR_USER,
        blank=False,
        null=False,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=s.MAX_LENGHT_FOR_USER,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=s.MAX_LENGHT_FOR_USER,
        blank=False,
        null=False,
    )
    password = models.CharField(
        'Пароль',
        max_length=s.MAX_LENGHT_FOR_USER,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}: {self.email}'


class Follow(models.Model):
    """Модель подписки."""
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followed',
        verbose_name='Автор, на которого подписаны'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('subscriber', 'author'),
                name='unique_follow'
            ),
        )

    def __str__(self):
        return f'Пользователь {self.subscriber} подписан на {self.author}'
