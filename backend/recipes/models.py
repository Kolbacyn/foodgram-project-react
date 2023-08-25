from django.db import models


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Уникальный слаг',
    )
    color = models.CharField(
        max_length=7,
        default="#ffffff",
        verbose_name='Цвет в HEX',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'slug', 'color'),
                name='unique_tag',
            ),
        )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
