from django.test import TestCase

from posts.models import Comment, Group, Follow, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='test_comment'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
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
            self.group: self.group.title,
            self.comment: self.comment.text[:Post.TEXT_SLICE_CUT],
            self.follow: f'Пользователь: {self.user},'
                         f' подписался на {self.author}'
        }
        for model, object_name in models_object_names.items():
            with self.subTest(field=model):
                self.assertEqual(object_name, str(model))

    def test_verbose_name(self):
        """Проверяем что verbose_name моделей совпадает с ожидаемым"""
        models = (self.post, self.group, self.comment, self.follow)
        verboses = ({'text': 'Текст поста',
                     'pub_date': 'Дата публикации',
                     'author': 'Автор',
                     'group': 'Группа'},
                    {'title': 'Название',
                     'description': 'Описание'},
                    {'post': 'Пост',
                     'author': 'Автор'},
                    {'user': 'Подписчик',
                     'author': 'Автор'})
        for model, verbose in zip(models, verboses):
            self.__check_verbose_names(model, verbose)

    def test_help_text(self):
        """Проверяем что help_text моделей совпадает с ожидаемым"""
        models = (self.post, self.comment)
        help_text = (
            {'text': 'Введите текст поста',
             'group': 'Группа, к которой будет относиться пост'},
            {'post': 'Пост, к которому относится комментарий',
             'author': 'Автор, комментария'}
        )
        for model, help_text in zip(models, help_text):
            for field, expected_value in help_text.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).help_text,
                        expected_value
                    )
