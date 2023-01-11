from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post, User
from yatube.settings import AMOUNT_OF_POSTS

POSTS_RANGE = 14
AMOUNT = POSTS_RANGE - AMOUNT_OF_POSTS
AMOUNT_OF_POSTS = AMOUNT_OF_POSTS
TEST_USER_AUTHOR_USERNAME = 'test_author'
TEST_USER_FOLLOWER_USERNAME = 'test_follower'
UNEXISTING_PAGE_URL = '/unexisting_page/'
INDEX_URL = '/'
INDEX_REVERSE = reverse('posts:index')
CREATE_URL = '/create/'
CREATE_REVERSE = reverse('posts:post_create')
FOLLOW_URL = '/follow/'
FOLLOW_REVERSE = reverse('posts:follow_index')


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_author')
        cls.follower = User.objects.create_user(username='test_follower')
        cls.first_group = Group.objects.create(
            title='First Group',
            slug='first-group',
            description='Contains posts with first IDs'
        )
        cls.left_group = Group.objects.create(
            title='Least Group',
            slug='Left-group',
            description='Contains posts with left IDs'
        )
        cls.posts_left_group = Post.objects.bulk_create(
            [Post(
                text=f'Test text of Post №{i}',
                author=cls.author,
                group=cls.left_group
            ) for i in range(1, POSTS_RANGE)]
        )
        cls.posts = Post.objects.create(
            text='First Group Post',
            author=cls.author,
            group=cls.first_group
        )
        cls.comment = Comment.objects.create(
            post=cls.posts,
            author=cls.author,
            text='test_comment'
        )
        cls.authors_client = Client()
        cls.followers_client = Client()
        cls.guest_client = Client()
        cls.authors_client.force_login(cls.author)
        cls.followers_client.force_login(cls.follower)
        cls.FIRST_GROUP_URL = f'/group/{cls.first_group.slug}/'
        cls.FIRST_GROUP_REVERSE = reverse('posts:group_posts',
                                          args=[
                                              cls.first_group.slug])
        cls.LEFT_GROUP_REVERSE = reverse('posts:group_posts',
                                         args=[cls.left_group.slug])
        cls.PROFILE_URL = f'/profile/{cls.author.username}/'
        cls.PROFILE_REVERSE = reverse('posts:profile',
                                      args=[cls.author.username])
        cls.POST_DETAIL_URL = f'/posts/{cls.posts.pk}/'
        cls.POST_DETAIL_REVERSE = reverse('posts:post_detail',
                                          args=[cls.posts.pk])
        cls.POST_EDIT_URL = f'/posts/{cls.posts.pk}/edit/'
        cls.POST_EDIT_REVERSE = reverse('posts:post_edit',
                                        args=[cls.posts.pk])
        cls.COMMENT_URL = f'/posts/{cls.posts.pk}/comment/'
        cls.COMMENT_REVERSE = reverse('posts:add_comment',
                                      args=[cls.posts.pk])
        cls.PROFILE_FOLLOW_URL = f'/profile/{cls.author.username}/follow/'
        cls.PROFILE_FOLLOW_REVERSE = reverse('posts:profile_follow',
                                             args=[cls.author.username])
        cls.PROFILE_UNFOLLOW_URL = f'/profile/{cls.author.username}/unfollow/'
        cls.PROFILE_UNFOLLOW_REVERSE = reverse('posts:profile_unfollow',
                                               args=[cls.author.username])
        cls.GUEST_EDIT_REDIRECT_TO_LOGIN_URL = (f'/auth/login/?next='
                                                f'{cls.POST_EDIT_URL}')
        cls.GUEST_CREATE_REDIRECT_TO_LOGIN_URL = (
            f'/auth/login/?next={CREATE_URL}'
        )
        cls.GUEST_COMMENT_REDIRECT_TO_LOGIN_URL = (
            f'/auth/login/?next={cls.COMMENT_URL}'
        )
