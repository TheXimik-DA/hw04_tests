from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата поста',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        null=True,
        blank=True,
        help_text='Укажите группу поста',
        verbose_name='Группа поста',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.text[:15]
