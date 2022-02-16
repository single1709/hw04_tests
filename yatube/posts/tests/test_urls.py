from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='no_name')

        # Создаем авторизованного пользователя и автора
        cls.author = User.objects.create_user(username='author')
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.author)

        # Создаем авторизованного пользователя
        cls.no_author = User.objects.create_user(username='no_author')
        cls.authorized_client_no_author = Client()
        cls.authorized_client_no_author.force_login(cls.no_author)

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            description='Тестовое описание группы',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )

        # шаблоны страниц доступные неавторизованному пользователю
        cls.templates_url_names_guest_client = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': f'/profile/{cls.user}/',
            'posts/post_detail.html': f'/posts/{cls.post.id}/',
        }

    def test_unexisting_page(self):
        """Проверка несуществующей страницы"""
        response = self.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_authorized_client_author(self):
        """Проверка доступности URL-адреса для авторизованного пользователя и автора"""
        response = self.authorized_client_author.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_urls_authorized_client(self):
        """Проверка доступности URL-адреса для авторизованного пользователя"""
        response = self.authorized_client_no_author.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_urls_guest_client(self):
        """Проверка доступности URL-адресов для неавторизованного пользователя"""
        for template, address in self.templates_url_names_guest_client.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """Проверка, что URL-адреса используют соответствующий шаблон"""

        # неавторизованный пользователь
        for template, address in self.templates_url_names_guest_client.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

        # авторизованный пользователь
        response = self.authorized_client_no_author.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_edit_post.html')

        # авторизованный пользователь-автор
        response = self.authorized_client_author.get(f'/posts/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_edit_post.html')
