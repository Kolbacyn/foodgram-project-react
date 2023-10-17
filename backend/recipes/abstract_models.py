from django.db import models

from users.models import User


class AbstractModelForCartAndFavorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        null=True
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Добавленный рецепт'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} added {self.recipe}'
