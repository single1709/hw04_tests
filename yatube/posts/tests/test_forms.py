from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Post, Group

User = get_user_model()


class TaskCreateFormTests(TestCase):
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
            group=cls.group,
        )

    def test_create_post(self):
        """Проверка формы создания поста"""

        posts_count = Post.objects.count()

        context = {
            'group': self.group.id,
            'text': 'Тестовый текст',
        }

        response = self.authorized_client_author.post(
            reverse('posts:post_create'),
            context,
        )

        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.author.username})
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1
        )

        new_post = Post.objects.order_by('id').last()
        self.assertEqual(new_post.text, self.post.text)
        self.assertEqual(new_post.author, self.post.author)
        self.assertEqual(new_post.group, self.post.group)

    def test_edit_post(self):
        """Проверка формы редактирования поста"""

        context = {
            'group': self.group.id,
            'text': 'Тестовый текст 2',
        }

        response = self.authorized_client_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            context,
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

        edit_post = Post.objects.get(id=self.post.id)
        self.assertTrue(
            edit_post.text != self.post.text or
            edit_post.group != self.post.group or
            edit_post.author != self.post.author
        )
