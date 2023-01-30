from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Название", max_length=200)
    slug = models.SlugField("Название группы", unique=True)
    description = models.TextField("Описание")

    class Meta:
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста',
    )
    image = models.ImageField(
        'Картинка',
        help_text='Загрузите подходящую картинку',
        upload_to='posts/',
        blank=True,
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        null=True,
        blank=True,
        help_text='Укажите группу для поста',
        verbose_name='Группа поста',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name='Комментарии'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор публикации'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Напишите комментарий',
    )
    created = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:15]
