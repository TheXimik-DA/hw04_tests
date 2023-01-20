from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='Тестовый слаг',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_model_group_has_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = self.group
        self.assertEqual(group.title, str(group))
        post = self.post
        self.assertEqual(post.text[:15], str(post))
        group = self.group
        self.assertEqual(group.title, str(group))
        post = self.post
        self.assertEqual(post.text[:15], str(post))

    def test_verbose_name(self):
        """verbose_name в полях сопадает с ожидаемым."""
        post = self.post
        fields = {
            post._meta.get_field('group').verbose_name: 'Группа поста',
            post._meta.get_field('text').verbose_name: 'Текст поста',
            post._meta.get_field('text').help_text: 'Введите текст поста',
            post._meta.get_field('author').verbose_name: 'Автор поста',
        }
        for field, text in fields.items():
            with self.subTest():
                self.assertEqual(field, text)

    def test_help_text(self):
        """help_text в полях сопадает с ожидаемым."""
        post = self.post
        fields = {
            post._meta.get_field('group').help_text: 'Укажите группу поста',
            post._meta.get_field('text').help_text: 'Введите текст поста',
        }
        for field, text in fields.items():
            with self.subTest():
                self.assertEqual(field, text)
