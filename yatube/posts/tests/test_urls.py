from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


REVERSE_URL_INDEX = reverse('posts:index')
REVERSE_URL_GROUP = reverse('posts:group_list', args=['test_slug'])
REVERSE_URL_AUTHOR_PROFILE = reverse('posts:profile', args=['tigr'])
REVERSE_URL_CREATE_POST = reverse('posts:post_create')


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='mostr')
        cls.author = User.objects.create_user(username='tigr')
        cls.group = Group.objects.create(
            title='Группа',
            slug='test_slug',
            description='Проверка описания'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group
        )
        cls.DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.post.id]
        )
        cls.EDIT_URL = reverse(
            'posts:post_edit', args=[cls.post.id]
        )
        cls.TEMPLATE = {
            REVERSE_URL_INDEX: 'posts/index.html',
            REVERSE_URL_GROUP: 'posts/group_list.html',
            REVERSE_URL_AUTHOR_PROFILE: 'posts/profile.html',
            PostURLTests.DETAIL_URL: 'posts/post_detail.html',
            PostURLTests.EDIT_URL: 'posts/create_post.html',
            REVERSE_URL_CREATE_POST: 'posts/create_post.html',
        }

    def test_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in PostURLTests.TEMPLATE.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Неверный шаблон - {template} для {url}',
                )

    def test_redirect_anonymous(self):
        """Cервер возвращает код 404, если страница не найдена."""
        response = self.authorized_client.get('/Supermario_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.author)

    def test_http_statuses(self):
        httpstatuses = [
            [REVERSE_URL_CREATE_POST, HTTPStatus.OK, self.authorized_client],
            [REVERSE_URL_GROUP, HTTPStatus.OK, self.guest_client],
            [REVERSE_URL_INDEX, HTTPStatus.OK, self.guest_client],
            [REVERSE_URL_CREATE_POST, HTTPStatus.FOUND, self.guest_client],
            [PostURLTests.DETAIL_URL, HTTPStatus.OK, self.guest_client],
            [REVERSE_URL_AUTHOR_PROFILE, HTTPStatus.OK, self.guest_client],
            [PostURLTests.EDIT_URL, HTTPStatus.FOUND, self.guest_client],
            [
                PostURLTests.EDIT_URL,
                HTTPStatus.FOUND,
                self.authorized_client,
            ],
            [PostURLTests.EDIT_URL, HTTPStatus.OK, self.author_client],
        ]
        for test in httpstatuses:
            adress, status, client = test
            self.assertEqual(
                client.get(adress).status_code,
                status,
                f'{adress} Возвращает другой статус, а не {status}',
            )

    def test_test_redirects(self):
        """
        Проверка перенаправления на страницу авторизации.
        Авторизованного пользователя перенаправляют на страницу с постом.
        """
        address_redirect_client = [
            [
                REVERSE_URL_CREATE_POST,
                f'/auth/login/?next={REVERSE_URL_CREATE_POST}',
                self.guest_client,
            ],
            [
                PostURLTests.EDIT_URL,
                f'/auth/login/?next={PostURLTests.EDIT_URL}',
                self.guest_client,
            ],
            [
                PostURLTests.EDIT_URL,
                PostURLTests.DETAIL_URL,
                self.authorized_client,
            ],
        ]
        for url, redirect_address, client in address_redirect_client:
            with self.subTest(url=url, client=client):
                response = client.get(url, follow=True)
                self.assertRedirects(response, redirect_address)
