from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from .test_config import (CREATE_REVERSE, INDEX_REVERSE,
                          CREATE_URL, INDEX_URL, UNEXISTING_PAGE_URL)


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user
        )
        cls.guest = User.objects.create_user(username='guest')
        cls.guest_client = Client()
        cls.authorized_client_author = Client()
        cls.authorized_client_not_author = Client()
        cls.authorized_client_author.force_login(cls.user)
        cls.authorized_client_not_author.force_login(cls.guest)
        cls.GROUP_URL = f'/group/{PostUrlTests.group.slug}/'
        cls.GROUP_REVERSE = reverse('posts:group_posts',
                                    args=[PostUrlTests.group.slug])
        cls.PROFILE_URL = f'/profile/{PostUrlTests.user.username}/'
        cls.PROFILE_REVERSE = reverse('posts:profile',
                                      args=[PostUrlTests.user.username])
        cls.POST_DETAIL_URL = f'/posts/{PostUrlTests.post.pk}/'
        cls.POST_DETAIL_REVERSE = reverse('posts:post_detail',
                                          args=[PostUrlTests.post.pk])
        cls.POST_EDIT_URL = f'/posts/{PostUrlTests.post.pk}/edit/'
        cls.POST_EDIT_REVERSE = reverse('posts:post_edit',
                                        args=[PostUrlTests.post.pk])
        cls.GUEST_EDIT_REDIRECT_TO_LOGIN_URL = (
            f'/auth/login/?next='
            f'{cls.POST_EDIT_URL}'
        )
        cls.GUEST_CREATE_REDIRECT_TO_LOGIN_URL = (
            f'/auth/login/?next={CREATE_URL}'
        )
        cls.COMMENT_URL = f'{cls.POST_DETAIL_URL}comment/'
        cls.GUEST_COMMENT_REDIRECT_TO_LOGIN_URL = (
            f'/auth/login/?next={cls.COMMENT_URL}'
        )

    def test_url_exists_desired_location(self):
        """Страница по конкретному адресу отдает соответсвующий http статус"""
        cases = (
            (INDEX_URL, self.guest_client, HTTPStatus.OK),
            (self.GROUP_URL, self.guest_client, HTTPStatus.OK),
            (self.PROFILE_URL, self.authorized_client_author, HTTPStatus.OK),
            (self.POST_DETAIL_URL, self.guest_client, HTTPStatus.OK),
            (self.POST_EDIT_URL, self.authorized_client_author, HTTPStatus.OK),
            (CREATE_URL, self.authorized_client_not_author, HTTPStatus.OK),
            (UNEXISTING_PAGE_URL, self.guest_client, HTTPStatus.NOT_FOUND)
        )
        for url, client, response_code in cases:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code,
                                 response_code, url)

    def test_page_gives_correct_redirect_after_response(self):
        """Страница перенаправляет пользователя"""
        cases = (
            (self.POST_EDIT_URL, self.guest_client,
             self.GUEST_EDIT_REDIRECT_TO_LOGIN_URL),
            (self.POST_EDIT_URL, self.authorized_client_not_author,
             self.POST_DETAIL_URL),
            (CREATE_URL, self.guest_client,
             self.GUEST_CREATE_REDIRECT_TO_LOGIN_URL),
            (self.COMMENT_URL, self.guest_client,
             self.GUEST_COMMENT_REDIRECT_TO_LOGIN_URL),
        )
        for url, client, redirect in cases:
            with self.subTest(url=url, client=client):
                self.assertRedirects(client.get(url, follow=True), redirect)

    def test_posts_uses_correct_template(self):
        """URL-адрес использует соответсвующий шаблон posts"""
        page_names_templates = {
            INDEX_REVERSE: 'posts/index.html',
            self.GROUP_REVERSE: 'posts/group_list.html',
            self.PROFILE_REVERSE: 'posts/profile.html',
            self.POST_DETAIL_REVERSE: 'posts/post_detail.html',
            CREATE_REVERSE: 'posts/post_create.html',
            self.POST_EDIT_REVERSE: 'posts/post_create.html'
        }
        for reverse_name, template in page_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)
