from django.test import TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from .test_config import (CREATE_REVERSE, FOLLOW_REVERSE,
                          FOLLOW_URL, INDEX_REVERSE,
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
        cls.GROUP_URL = f'/group/{cls.group.slug}/'
        cls.GROUP_REVERSE = reverse('posts:group_posts',
                                    args=[cls.group.slug])
        cls.PROFILE_URL = f'/profile/{cls.user.username}/'
        cls.PROFILE_REVERSE = reverse('posts:profile',
                                      args=[cls.user.username])
        cls.POST_DETAIL_URL = f'/posts/{cls.post.pk}/'
        cls.POST_DETAIL_REVERSE = reverse('posts:post_detail',
                                          args=[cls.post.pk])
        cls.POST_EDIT_URL = f'/posts/{cls.post.pk}/edit/'
        cls.POST_EDIT_REVERSE = reverse('posts:post_edit',
                                        args=[cls.post.pk])
        cls.COMMENT_URL = f'/posts/{cls.post.pk}/comment/'
        cls.COMMENT_REVERSE = reverse('posts:add_comment',
                                      args=[cls.post.pk])
        cls.PROFILE_FOLLOW_URL = f'/profile/{cls.user.username}/follow/'
        cls.PROFILE_FOLLOW_REVERSE = reverse('posts:profile_follow',
                                             args=[cls.user.username])
        cls.PROFILE_UNFOLLOW_URL = f'/profile/{cls.user.username}/unfollow/'
        cls.PROFILE_UNFOLLOW_REVERSE = reverse('posts:profile_unfollow',
                                               args=[cls.user.username])

    def test_routes_return_correct_url(self):
        url_names_routes = {
            INDEX_URL: INDEX_REVERSE,
            self.GROUP_URL: self.GROUP_REVERSE,
            self.PROFILE_URL: self.PROFILE_REVERSE,
            self.POST_DETAIL_URL: self.POST_DETAIL_REVERSE,
            CREATE_URL: CREATE_REVERSE,
            self.POST_EDIT_URL: self.POST_EDIT_REVERSE,
            self.COMMENT_URL: self.COMMENT_REVERSE,
            FOLLOW_URL: FOLLOW_REVERSE,
            self.PROFILE_FOLLOW_URL: self.PROFILE_FOLLOW_REVERSE,
            self.PROFILE_UNFOLLOW_URL: self.PROFILE_UNFOLLOW_REVERSE
        }
        for url, route in url_names_routes.items():
            with self.subTest(url=url):
                self.assertEqual(url, route)
