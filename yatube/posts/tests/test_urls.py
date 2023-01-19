from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='TheXimik_',
            password='1!21%321',
            email='tool@gmail.com',
        )
        cls.group = Group.objects.create(
            slug='slug_test',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
        )

    def setUp(self):
        self.authorizated_client = Client()
        self.authorizated_client.force_login(self.author)
        self.nonauthorized_client = Client()

    def test_home_page(self):
        """Главная страница доступна любому пользователю."""
        response = self.nonauthorized_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_page(self):
        """Страница группы доступна любому пользователю."""
        response = self.nonauthorized_client.get('/group/slug_test/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_page(self):
        """Профильная страница пользователя доступна любому пользователю."""
        response = self.nonauthorized_client.get('/profile/TheXimik_/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail(self):
        """Страница поста доступна любому пользователю."""
        response = self.nonauthorized_client.get('/posts/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create(self):
        """Cоздание поста доступно только авторизованному пользователю."""
        response = self.authorizated_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """Страница редактирования поста доступно только его автору."""
        response = self.authorizated_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        """URL-адрес использует корректный шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/slug_test/',
            'posts/profile.html': '/profile/TheXimik_/',
            'posts/post_detail.html': '/posts/1/',
            'posts/create_post.html': '/posts/1/edit/',
            'posts/create_post.html': '/create/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorizated_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_returns_404(self):
        """Несуществующая страница вернёт ошибку 404."""
        response = self.nonauthorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
