from django.test import TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from .test_config import (CREATE_REVERSE, INDEX_REVERSE,
                          CREATE_URL, INDEX_URL)


class PostRoutesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user
        )
        cls.GROUP_URL = f'/group/{PostRoutesTest.group.slug}/'
        cls.GROUP_REVERSE = reverse('posts:group_posts',
                                    args=[PostRoutesTest.group.slug])
        cls.PROFILE_URL = f'/profile/{PostRoutesTest.user.username}/'
        cls.PROFILE_REVERSE = reverse('posts:profile',
                                      args=[PostRoutesTest.user.username])
        cls.POST_DETAIL_URL = f'/posts/{PostRoutesTest.post.pk}/'
        cls.POST_DETAIL_REVERSE = reverse('posts:post_detail',
                                          args=[PostRoutesTest.post.pk])
        cls.POST_EDIT_URL = f'/posts/{PostRoutesTest.post.pk}/edit/'
        cls.POST_EDIT_REVERSE = reverse('posts:post_edit',
                                        args=[PostRoutesTest.post.pk])

    def test_routes_return_correct_url(self):
        url_names_routes = {
            INDEX_URL: INDEX_REVERSE,
            self.GROUP_URL: self.GROUP_REVERSE,
            self.PROFILE_URL: self.PROFILE_REVERSE,
            self.POST_DETAIL_URL: self.POST_DETAIL_REVERSE,
            CREATE_URL: CREATE_REVERSE,
            self.POST_EDIT_URL: self.POST_EDIT_REVERSE
        }
        for url, route in url_names_routes.items():
            with self.subTest(url=url):
                self.assertEqual(url, route)
