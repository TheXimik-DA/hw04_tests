from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_author = Client()
        cls.author = User.objects.create_user(username='tigr')
        cls.authorized_author.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.grouptwo = Group.objects.create(
            title='Тестовая группа2',
            description='Тестовое описание2',
            slug='test-slug2',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.nonauthorized_client = Client()

    def test_create_post(self):
        """Валидная форма создает запись в post."""
        old_posts = Post.objects.all().values_list('id', flat=True)
        form_data = {
            'text': 'Пост, созданный через форму',
            'group': self.group.pk,
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        new_posts = Post.objects.exclude(
            id__contains=old_posts).values('text', 'group', 'author')
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.author}))
        self.assertEqual(new_posts.count(), 1)
        self.assertEqual(new_posts[0]['group'], form_data['group'])
        self.assertEqual(new_posts[0]['text'], form_data['text'])
        self.assertEqual(new_posts[0]['author'], self.author.pk)

    def test_edit_post(self):
        """Валидная форма перезаписывает запись."""
        form_data = {
            'text': 'Измененный текст',
            'group': self.grouptwo.pk,
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.pk}))
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.author,
                group=self.grouptwo,
            ).exists()
        )

    def test_guest_can_not_create_new_post(self):
        """При попытке создать новую запись неавторизованный клиент
        перенаправляется на страницу авторизации a запись не производится.
        """
        form_data = {
            'text': 'Измененный текст',
            'group': self.grouptwo.pk,
        }
        response = self.nonauthorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), 1)
