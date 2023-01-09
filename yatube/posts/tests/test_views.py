from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User
from yatube.settings import AMOUNT_OF_POSTS
from .test_config import INDEX_REVERSE

POSTS_RANGE = 14


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AMOUNT = POSTS_RANGE - AMOUNT_OF_POSTS
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
        cls.follows = Follow.objects.create(user=cls.follower,
                                            author=cls.author)
        cls.authors_client = Client()
        cls.follower_client = Client()
        cls.authors_client.force_login(cls.author)
        cls.follower_client.force_login(cls.follower)
        cls.LEFT_GROUP_REVERSE = reverse('posts:group_posts',
                                         args=[cls.left_group.slug])
        cls.FIRST_GROUP_REVERSE = reverse('posts:group_posts',
                                          args=[
                                              cls.first_group.slug])
        cls.PROFILE_REVERSE = reverse('posts:profile',
                                      args=[cls.author.username])
        cls.POST_DETAIL_REVERSE = reverse('posts:post_detail',
                                          args=[cls.posts.pk])
        cls.POST_EDIT_REVERSE = reverse('posts:post_edit',
                                        args=[cls.posts.pk])
        cls.FOLLOW_INDEX_REVERSE = reverse('posts:follow_index')
        cls.PROFILE_FOLLOW_REVERSE = reverse('posts:profile_follow',
                                             args=[cls.author.username])
        cls.PROFILE_UNFOLLOW_REVERSE = reverse('posts:profile_unfollow',
                                               args=[cls.author.username])

    def test_first_page_contains_expecting_amount_of_posts(self):
        """Удостоверимся, что на первую страницу передаётся
         ожидаемое количество объектов.
        """
        responses = (
            self.authors_client.get(
                INDEX_REVERSE
            ),
            self.authors_client.get(self.LEFT_GROUP_REVERSE),
            self.authors_client.get(self.PROFILE_REVERSE)
        )
        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(
                    len(response.context['page_obj'].object_list),
                    AMOUNT_OF_POSTS)

    def test_last_page_contains_expecting_amount_of_posts(self):
        """Удостоверимся, что на последнюю страницу передаётся
         ожидаемое количество объектов.
        """
        routes_amounts = {
            INDEX_REVERSE: self.AMOUNT,
            self.LEFT_GROUP_REVERSE:
                self.left_group.posts.all().count() - AMOUNT_OF_POSTS,
            self.PROFILE_REVERSE: self.AMOUNT
        }
        for route, amount in routes_amounts.items():
            with self.subTest(route=route):
                response = self.authors_client.get(route)
                last_page = response.context['page_obj'].end_index()
                response = self.authors_client.get(
                    route + f'?page={last_page}')
                self.assertEqual(
                    len(response.context['page_obj'].object_list), amount)

    def test_post_from_all_routes_show_correct_context(self):
        """Проверка контекста поста для страниц со списком постов"""
        routes_keys = {
            self.authors_client.get(INDEX_REVERSE): 'page_obj',
            self.authors_client.get(self.FIRST_GROUP_REVERSE):
                'page_obj',
            self.authors_client.get(self.PROFILE_REVERSE):
                'page_obj',
            self.authors_client.get(self.POST_DETAIL_REVERSE):
                'post'
        }
        for route, key in routes_keys.items():
            with self.subTest(route=route):
                first_object = (route.context[key][0] if key != 'post'
                                else route.context[key])
                self.assertEqual(
                    first_object.text[:Post.TEXT_SLICE_CUT],
                    self.posts.text[:Post.TEXT_SLICE_CUT])
                self.assertEqual(first_object.author, self.author)
                self.assertEqual(first_object.pub_date,
                                 self.posts.pub_date)
                self.assertEqual(first_object.group, self.posts.group)
                self.assertEqual(first_object.image, self.posts.image)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authors_client.get(
            self.FIRST_GROUP_REVERSE
        )
        group = response.context['group']
        self.assertEqual(group.title,
                         self.first_group.title)
        self.assertEqual(group.slug,
                         self.first_group.slug)
        self.assertEqual(group.description,
                         self.first_group.description)

    def test_concrete_post_on_pages(self):
        """Конкретный пост с определённой группой отображается на определенной
        странице
        """
        responses = (
            self.authors_client.get(INDEX_REVERSE),
            self.authors_client.get(self.FIRST_GROUP_REVERSE),
            self.authors_client.get(self.PROFILE_REVERSE)
        )
        for response in responses:
            with self.subTest(response=response):
                self.assertIn(
                    self.posts,
                    response.context['page_obj'].paginator.object_list)

    def test_cache_works_correctly(self):
        response = self.authors_client.get(INDEX_REVERSE)
        content_before = response.content
        Post.objects.get(id=self.posts.pk).delete()
        self.assertEqual(content_before,
                         self.authors_client.get(INDEX_REVERSE).content)
        cache.clear()
        response_after_clear = self.authors_client.get(INDEX_REVERSE)
        content_after = response_after_clear.content
        self.assertNotEqual(content_before, content_after)

    def test_authorized_user_can_follow_unfollow_authors(self):
        self.follower_client.get(self.PROFILE_FOLLOW_REVERSE)
        self.assertTrue(Follow.objects.all().exists())
        self.follower_client.get(self.PROFILE_UNFOLLOW_REVERSE)
        self.assertFalse(Follow.objects.all().exists())

    def test_authorized_user_can_see_followed_author_posts(self):
        self.follower_client.get(self.PROFILE_FOLLOW_REVERSE)
        response = self.follower_client.get(self.FOLLOW_INDEX_REVERSE)
        self.assertEqual(response.context['page_obj'][0].pk, self.posts.pk)
