from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UsernameField
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testUser')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(UsersURLTest.user)

    def test_signup_url_exists_at_desired_location(self):
        """Страница '/auth/signup/' доступна любому пользователю"""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_exists_at_desired_location(self):
        """Страница '/auth/logout/' доступна любому пользователю"""
        response = self.guest_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_url_exists_at_desired_location(self):
        """Страница '/auth/login/' доступна любому пользователю"""
        response = self.guest_client.get('/auth/login/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_exists_at_desired_location(self):
        """Страница '/auth/password_reset/' доступна любому пользователю"""
        response = self.guest_client.get('/auth/password_reset/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done_exists_at_desired_location(self):
        """Страница '/auth/password_reset/done/'
         доступна любому пользователю
         """
        response = self.guest_client.get('/auth/password_reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_confirm_exists_at_desired_location(self):
        """Страница '/auth/reset/<uidb64>/<token>/'
        доступна любому пользователю
        """
        response = self.guest_client.get('/auth/reset/<uidb64>/<token>/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_complete_exists_at_desired_location(self):
        """Страница '/reset/done/' доступна любому пользователю"""
        response = self.guest_client.get('/auth/reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_exists_at_desired_location(self):
        """Страница '/auth/password_change/'
        доступна авторизованному пользователю
        """
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_exists_at_desired_location(self):
        """Страница '/auth/password_change/done/'
        доступна авторизованному пользователю
        """
        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_redirects_anonymous_to_login(self):
        """Страница '/auth/password_change/' перенаправит анонимного
         пользователя на страницу логина.
        """
        response = self.guest_client.get('/auth/password_change/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/auth/password_change/')

    def test_password_change_done_redirects_anonymous_to_login(self):
        """Страница '/auth/password_change/done/' перенаправит анонимного
         пользователя на страницу логина.
        """
        response = self.guest_client.get(
            '/auth/password_change/done/', follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/auth/password_change/done/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон users."""
        templates_url_names = {
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/',
            'users/password_reset_form.html': '/auth/password_reset/',
            'users/password_reset_done.html': '/auth/password_reset/done/',
            'users/password_reset_confirm.html':
                '/auth/reset/<uidb64>/<token>/',
            'users/password_reset_complete.html': '/auth/reset/done/',
            'users/password_change_form.html': '/auth/password_change/',
            'users/password_change_done.html': '/auth/password_change/done/',
            'users/logged_out.html': '/auth/logout/'
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)


class UsersViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testUser')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(UsersViewsTest.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон users."""
        templates_url_names = {
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('users:login'),
            'users/password_reset_form.html': reverse('users:password_reset'),
            'users/password_reset_confirm.html':
                reverse('users:password_reset_confirm',
                        kwargs={'uidb64': 'uidb64', 'token': 'token'}),
            'users/password_reset_done.html':
                reverse('users:password_reset_done'),
            'users/password_reset_complete.html':
                reverse('users:password_reset_complete'),
            'users/password_change_form.html':
                reverse('users:password_change_form'),
            'users/password_change_done.html':
                reverse('users:password_change_done'),
            'users/logged_out.html': reverse('users:logout')
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_page_shows_correct_context(self):
        """Страница reverse('users:signup') в контексте передаётся форма
         для создания нового пользователя.
        """
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': UsernameField,
            'email': forms.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertEqual(type(form_field), expected)


class UsersCreateFormTest(TestCase):
    """Валидная форма создает пост"""
    def setUp(self):
        self.guest_client = Client()

    def test_users_form_create_user(self):
        user_count = User.objects.all().count()
        form_data = {
            'first_name': 'Test',
            'last_name': 'Django',
            'username': 'test_user',
            'email': 'test_user@gmail.com',
            'password1': 'ducdwtVJLftTJV8',
            'password2': 'ducdwtVJLftTJV8'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.all().count(), user_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='test_user',
                email='test_user@gmail.com',
            )
        )
