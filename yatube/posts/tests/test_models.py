from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def __check_verbose_names(self, model, dict_of_verboses):
        for field, expected_value in dict_of_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    model._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_models_have_correct_object_name(self):
        """Проверяем, что у моделей корректно работает __str__"""
        models_object_names = {
            self.post: self.post.text[:Post.TEXT_SLICE_CUT],
            self.group: self.group.title
        }
        for model, object_name in models_object_names.items():
            with self.subTest(field=model):
                self.assertEqual(object_name, str(model))

    def test_verbose_name(self):
        """Проверяем что verbose_name моделей совпадает с ожидаемым"""
        models = (self.post, self.group)
        verboses = ({'text': 'Текст поста',
                     'pub_date': 'Дата публикации',
                     'author': 'Автор',
                     'group': 'Группа'},
                    {'title': 'Название',
                     'description': 'Описание'})
        for model, verbose in zip(models, verboses):
            self.__check_verbose_names(model, verbose)

    def test_help_text(self):
        """Проверяем что help_text моделей совпадает с ожидаемым"""
        post_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in post_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text,
                    expected_value
                )
