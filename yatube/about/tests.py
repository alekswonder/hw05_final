from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_url_exists_at_desired_location(self):
        """Страница '/author/' доступна любому пользователю"""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_url_exists_at_desired_location(self):
        """Страница '/tech/' доступна любому пользователю"""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон about"""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_use_correct_templates_by_name(self):
        """URL-адрес, генерируемый при помощи имени,
         использует соответствующий шаблон about
         """
        templates_page_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(templatet=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
