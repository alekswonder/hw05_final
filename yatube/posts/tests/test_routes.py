from .test_config import (BaseTestCase, CREATE_REVERSE, CREATE_URL,
                          FOLLOW_REVERSE, FOLLOW_URL, INDEX_REVERSE, INDEX_URL)


class PostRoutesTest(BaseTestCase):
    def test_routes_return_correct_url(self):
        url_names_routes = {
            INDEX_URL: INDEX_REVERSE,
            self.FIRST_GROUP_URL: self.FIRST_GROUP_REVERSE,
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
