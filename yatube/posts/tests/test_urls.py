from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

CONST_INDEX = reverse('posts:index')
CONST_NEW_POST = reverse('posts:post_create')
CONST_USER = 'TIGR'
CONST_USER2 = 'monstr'
CONST_AUTH = reverse('login')
CONST_SLUG = 'test_group'
CONST_GROUP_URL = reverse('posts:group_list', kwargs={'slug': CONST_SLUG})
CONST_PROFILE_URL = reverse('posts:profile', kwargs={'username': CONST_USER})
CONST_LOGIN_CREATE = f'{CONST_AUTH}?next={CONST_NEW_POST}'


class UrlsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=CONST_USER)
        cls.group = Group.objects.create(
            title='ТЕСТОВЫЙ ТАЙТЛ',
            slug=CONST_SLUG,
            description='ТЕСТОВОЕ ОПИСАНИЕ'
        )
        cls.post = Post.objects.create(
            text='ТЕСТОВЫЙ ТЕКСТ',
            author=cls.user,
            group=cls.group
        )
        cls.user2 = User.objects.create(username=CONST_USER2)
        cls.POST_URL = reverse(
            'posts:post_detail',
            args=[cls.post.id])
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            args=[cls.post.id])
        cls.LOGIN_EDIT_POST = f'{CONST_AUTH}?next={cls.POST_EDIT_URL}'

    def setUp(self):
        self.guest = Client()
        self.author = Client()
        self.author.force_login(self.user)
        self.another = Client()
        self.another.force_login(self.user2)

    def test_urls_uses_correct_template(self):
        template_urls_names = [
            ['posts/index.html', CONST_INDEX],
            ['posts/create_post.html', CONST_NEW_POST],
            ['posts/group_list.html', CONST_GROUP_URL],
            ['posts/post_detail.html', self.POST_URL],
            ['posts/profile.html', CONST_PROFILE_URL],
            ['posts/create_post.html', self.POST_EDIT_URL]
        ]
        for template, url in template_urls_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(self.author.get(url), template,)

    def test_urls_status_code(self):
        urls_names = [
            [self.POST_EDIT_URL, self.another, HTTPStatus.FOUND],
            [CONST_INDEX, self.guest, HTTPStatus.OK],
            [CONST_NEW_POST, self.guest, HTTPStatus.FOUND],
            [CONST_GROUP_URL, self.guest, HTTPStatus.OK],
            [self.POST_URL, self.guest, HTTPStatus.OK],
            [CONST_PROFILE_URL, self.guest, HTTPStatus.OK],
            [self.POST_EDIT_URL, self.guest, HTTPStatus.FOUND],
            [self.POST_EDIT_URL, self.author, HTTPStatus.OK],
            [CONST_NEW_POST, self.author, HTTPStatus.OK],
        ]
        for url, client, status in urls_names:
            with self.subTest(url=url, client=client, status=status,):
                self.assertEqual(client.get(url).status_code, status,)

    def test_redirect_urls_correct(self):
        urls = [
            [CONST_NEW_POST, self.guest, CONST_LOGIN_CREATE],
            [self.POST_EDIT_URL, self.guest, self.LOGIN_EDIT_POST],
            [self.POST_EDIT_URL, self.another, self.POST_URL],
        ]
        for url, client, redirect in urls:
            with self.subTest(url=url, client=client):
                self.assertRedirects(client.get(url, follow=True), redirect,)
