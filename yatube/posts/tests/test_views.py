from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='author')
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.author)

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            description='Тестовое описание группы',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )

    def test_pages_uses_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""

        templates_pages_names = (
            (reverse('posts:index'), 'posts/index.html'),
            (reverse('posts:post_create'), 'posts/create_edit_post.html'),
            (reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ), 'posts/group_list.html'),
            (reverse(
                'posts:profile',
                kwargs={'username': self.author}
            ), 'posts/profile.html'),
            (reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ), 'posts/post_detail.html'),
            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ), 'posts/create_edit_post.html'),
        )

        for reverse_name, template in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='author')
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.author)

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            description='Тестовое описание группы',
            slug='test-slug',
        )

        objs = (Post(
            text=f'Тестовый текст {i}',
            author=cls.author,
            group=cls.group,) for i in range(13)
        )
        cls.post = Post.objects.bulk_create(objs)

    def test_paginator(self):
        """Проверяем, что Paginator работает корректно"""

        pages_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.author.username})
        )

        for name_page in pages_names:
            with self.subTest(name_page=name_page):
                response = self.authorized_client_author.get(name_page)
                self.assertEqual(len(response.context['page_obj']), 10)

        for name_page in pages_names:
            with self.subTest(name_page=name_page):
                response = self.authorized_client_author.get(
                    name_page, {'page': 2}
                )
                self.assertEqual(len(response.context['page_obj']), 3)


class ContextViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='author')
        cls.author2 = User.objects.create_user(username='author2')
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.author2)

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            description='Тестовое описание группы',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст1',
            author=cls.author2,
            group=cls.group,
        )

    def test_correct_context_index(self):
        """Проверяем context index"""
        response = self.authorized_client_author.get(reverse('posts:index'))
        self.assertIsInstance(response.context['page_obj'][0], Post)

    def test_correct_context_group_list(self):
        """Проверяем context group_list"""
        response = self.authorized_client_author.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)

    def test_correct_context_profile(self):
        """Проверяем context profile"""
        response = self.authorized_client_author.get(
            reverse('posts:profile', kwargs={'username': self.author2.username})
        )
        self.assertEqual(response.context['author'], self.author2)

    def test_correct_context_post_detail(self):
        """Проверяем context post_detail"""
        response = self.authorized_client_author.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context['post'].text, self.post.text)

    def test_correct_context_post_edit(self):
        """Проверяем context post_edit"""
        response = self.authorized_client_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response.context['form'].initial['text'],
            self.post.text
        )

    def test_correct_context_post_create(self):
        """Проверяем context post_create"""
        response = self.authorized_client_author.get(
            reverse('posts:post_create')
        )
        self.assertIsInstance(response.context['form'], PostForm)


class CreatePostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='author')
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.author)

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            description='Тестовое описание группы',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст1',
            author=cls.author,
            group=cls.group,
        )

    def test_correct_post_create_index(self):
        """Проверяем что пост после создания появится на главной странице сайта,
        на странице выбранной группы,в профайле пользователя"""
        pages_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.author.username}),
        )

        for name_page in pages_names:
            with self.subTest(name_page=name_page):
                response = self.authorized_client_author.get(name_page)
                self.assertTrue(
                    response.context['page_obj'][0],
                    "Пост не появился на странице"
                )
