import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Test Group',
            slug='test-group',
            description='Test group description'
        )
        cls.edit_group = Group.objects.create(
            title='edit_group',
            slug='test-edit',
        )
        cls.post = Post.objects.create(
            text='Test text of Test Post',
            author=cls.user,
            group=cls.group,
            image=None
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.CREATE_REVERSE = reverse('posts:post_create')
        cls.POST_EDIT_REVERSE = reverse('posts:post_edit',
                                        args=[PostFormTests.post.pk])
        cls.POST_DETAIL_REVERSE = reverse('posts:post_detail',
                                          args=[PostFormTests.post.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_show_correct_context(self):
        """Шаблон create_form сформирован с правильным контекстом."""
        responses = {
            self.authorized_client.get(self.CREATE_REVERSE):
                'create',
            self.authorized_client.get(
                self.POST_EDIT_REVERSE): 'edit'
        }
        for response, act in responses.items():
            if act == 'create':
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.models.ModelChoiceField
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)
            elif act == 'edit':
                form_instance = response.context['form'].instance
                self.assertEqual(form_instance, self.post)

    def test_post_form_create_post(self):
        """Валидная форма создает пост"""
        posts_count = Post.objects.count()
        small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.jpg',
            content=small_jpg,
            content_type='image/jpg'
        )
        form_data = {
            'text': 'Test text',
            'group': self.group.pk,
            'image': uploaded
        }
        self.authorized_client.post(
            self.CREATE_REVERSE,
            data=form_data,
            follow=True
        )
        post = Post.objects.latest('pub_date')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(str(post.image), f'posts/{form_data["image"].name}')

    def test_post_form_edit_post(self):
        """Валидная форма редактирует пост"""
        post_count = Post.objects.all().count()
        form_data_edit = {
            'text': 'Edited',
            'group': self.edit_group.pk,
        }
        response = self.authorized_client.post(
            self.POST_EDIT_REVERSE,
            data=form_data_edit,
            follow=True
        )
        post = Post.objects.latest('pub_date')
        self.assertRedirects(response, self.POST_DETAIL_REVERSE)
        self.assertEqual(post_count, Post.objects.all().count())
        self.assertEqual(post.text,
                         form_data_edit['text'])
        self.assertEqual(post.group.id,
                         form_data_edit['group'])
        self.assertEqual(post.author, self.user)


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Test Group',
            slug='test-group',
            description='Test group description'
        )
        cls.post = Post.objects.create(
            text='Test text of Test Post',
            author=cls.user,
            group=cls.group,
            image=None
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(CommentFormTest.user)
        cls.POST_DETAIL_REVERSE = reverse('posts:post_detail',
                                          args=[CommentFormTest.post.pk])
        cls.ADD_COMMENT_REVERSE = reverse('posts:add_comment',
                                          args=[CommentFormTest.post.pk])

    def test_authorized_user_comment_post(self):
        comment_count = Comment.objects.all().count()
        comment_data = {
            'text': 'Test comment',
            'post': self.post,
            'author': self.user
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT_REVERSE,
            data=comment_data,
            follow=True
        )
        self.assertRedirects(
            response, self.POST_DETAIL_REVERSE
        )
        created_comment = Comment.objects.latest('created')
        self.assertEqual(Comment.objects.all().count(), comment_count + 1)
        self.assertEqual(created_comment.text, comment_data['text'])
        self.assertEqual(created_comment.post, comment_data['post'])
        self.assertEqual(created_comment.author, comment_data['author'])
        response = self.authorized_client.get(
            self.POST_DETAIL_REVERSE)
        comment = response.context['comments'][0]
        self.assertEqual(created_comment, comment)
