from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.not_author = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='Тестовый тайтл',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
        )
        cls.authorized_client_not_author = Client()
        cls.authorized_client_not_author.force_login(cls.not_author)

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username='tigr')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_and_group(self):
        """Главная страница и страница группы доступны всем"""
        url_names = (
            '/',
            '/group/test_slug/',
            '/profile/test_user/',
            f'/posts/{self.post.pk}/',
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_for_authorized(self):
        """Страница /create доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_url(self):
        """Без авторизации эти URL недоступны"""
        url_names = (
            '/create/',
            f'/posts/{self.post.pk}/edit/',
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_redirect_anonymous(self):
        """Cервер возвращает код 404, если страница не найдена."""
        response = self.authorized_client.get('/Supermario_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_no_author_of_post_cant_edit_post(self):
        """Страница редактирования не доступна
        авторизованному пользователю, но доступна автору поста"""
        response = self.authorized_client_not_author.get(
            f'/posts/{self.post.pk}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.pk}/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unknown_page_url_unexists_at_desired_location(self):
        """Страница не существует"""
        response = Client().get('/none/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/create_post.html': '/create/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ),
            'posts/profile.html': '/profile/test_user/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
