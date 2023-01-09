from django.test import Client, TestCase

from posts.tests.test_config import UNEXISTING_PAGE_URL


class CustomERRORPagesTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404_use_correct_template(self):
        response = self.guest_client.get(UNEXISTING_PAGE_URL)
        self.assertTemplateUsed(response, 'core/404.html')
