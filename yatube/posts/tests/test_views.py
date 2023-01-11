from django.core.cache import cache

from posts.models import Follow, Post
from .test_config import (AMOUNT, AMOUNT_OF_POSTS, BaseTestCase, INDEX_REVERSE,
                          FOLLOW_REVERSE)


class PostPagesTest(BaseTestCase):
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
            INDEX_REVERSE: AMOUNT,
            self.LEFT_GROUP_REVERSE:
                self.left_group.posts.all().count() - AMOUNT_OF_POSTS,
            self.PROFILE_REVERSE: AMOUNT
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
        self.followers_client.get(self.PROFILE_FOLLOW_REVERSE)
        self.assertTrue(Follow.objects.all().exists())
        self.followers_client.get(self.PROFILE_UNFOLLOW_REVERSE)
        self.assertFalse(Follow.objects.all().exists())

    def test_authorized_user_can_see_followed_author_posts(self):
        self.followers_client.get(self.PROFILE_FOLLOW_REVERSE)
        response = self.followers_client.get(FOLLOW_REVERSE)
        self.assertEqual(response.context['page_obj'][0].pk, self.posts.pk)
