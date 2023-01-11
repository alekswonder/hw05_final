from http import HTTPStatus

from .test_config import (BaseTestCase, CREATE_REVERSE, CREATE_URL,
                          INDEX_URL, INDEX_REVERSE, FOLLOW_REVERSE, FOLLOW_URL,
                          UNEXISTING_PAGE_URL)


class PostUrlTests(BaseTestCase):
    def test_url_exists_desired_location(self):
        """Страница по конкретному адресу отдает соответсвующий http статус"""
        cases = (
            (INDEX_URL, self.guest_client, HTTPStatus.OK),
            (self.FIRST_GROUP_URL, self.guest_client, HTTPStatus.OK),
            (self.PROFILE_URL, self.authors_client, HTTPStatus.OK),
            (self.POST_DETAIL_URL, self.guest_client, HTTPStatus.OK),
            (self.POST_EDIT_URL, self.authors_client, HTTPStatus.OK),
            (CREATE_URL, self.followers_client, HTTPStatus.OK),
            (UNEXISTING_PAGE_URL, self.guest_client, HTTPStatus.NOT_FOUND),
            (self.COMMENT_URL, self.followers_client,
             HTTPStatus.FOUND),
            (FOLLOW_URL, self.followers_client, HTTPStatus.OK),
            (self.PROFILE_FOLLOW_URL, self.followers_client,
             HTTPStatus.FOUND),
            (self.PROFILE_UNFOLLOW_URL, self.followers_client,
             HTTPStatus.FOUND),

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
            (self.POST_EDIT_URL, self.followers_client,
             self.POST_DETAIL_URL),
            (CREATE_URL, self.guest_client,
             self.GUEST_CREATE_REDIRECT_TO_LOGIN_URL),
            (self.COMMENT_URL, self.guest_client,
             self.GUEST_COMMENT_REDIRECT_TO_LOGIN_URL),
            (self.COMMENT_URL, self.followers_client,
             self.POST_DETAIL_URL),
            (self.PROFILE_FOLLOW_URL, self.followers_client,
             self.PROFILE_URL),
            (self.PROFILE_UNFOLLOW_URL, self.followers_client,
             self.PROFILE_URL),
        )
        for url, client, redirect in cases:
            with self.subTest(url=url, client=client):
                self.assertRedirects(client.get(url, follow=True), redirect)

    def test_posts_uses_correct_template(self):
        """URL-адрес использует соответсвующий шаблон posts"""
        page_names_templates = {
            INDEX_REVERSE: 'posts/index.html',
            self.FIRST_GROUP_REVERSE: 'posts/group_list.html',
            self.PROFILE_REVERSE: 'posts/profile.html',
            self.POST_DETAIL_REVERSE: 'posts/post_detail.html',
            CREATE_REVERSE: 'posts/post_create.html',
            self.POST_EDIT_REVERSE: 'posts/post_create.html',
            FOLLOW_REVERSE: 'posts/follow.html',
        }
        for reverse_name, template in page_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authors_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
