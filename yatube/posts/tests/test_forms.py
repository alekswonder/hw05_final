import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from posts.models import Comment, Post
from .test_config import CREATE_REVERSE, BaseTestCase

SMALL_JPG = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.jpg',
    content=SMALL_JPG,
    content_type='image/jpg'
)
UPLOADED_EDIT = SimpleUploadedFile(
    name='small_edit.jpg',
    content=SMALL_JPG,
    content_type='image/jpg'
)
PATH_TO_IMAGE = f'posts/{UPLOADED.name}'
PATH_TO_IMAGE_EDIT = f'posts/{UPLOADED_EDIT.name}'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(BaseTestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_show_correct_context(self):
        """Шаблон create_form сформирован с правильным контекстом."""
        responses = {
            self.authors_client.get(CREATE_REVERSE):
                'create',
            self.authors_client.get(
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
                self.assertEqual(form_instance, self.posts)

    def test_post_form_create_post(self):
        """Валидная форма создает пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'group': self.first_group.pk,
            'image': UPLOADED
        }
        self.authors_client.post(
            CREATE_REVERSE,
            data=form_data,
            follow=True
        )
        post = Post.objects.latest('pub_date')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.image, PATH_TO_IMAGE)

    def test_post_form_edit_post(self):
        """Валидная форма редактирует пост"""
        post_count = Post.objects.all().count()
        form_data_edit = {
            'text': 'Edited',
            'group': self.first_group.pk,
            'image': UPLOADED_EDIT
        }
        response = self.authors_client.post(
            self.POST_EDIT_REVERSE,
            data=form_data_edit,
            follow=True
        )
        post = Post.objects.get(text=form_data_edit['text'])

        self.assertRedirects(response, self.POST_DETAIL_REVERSE)
        self.assertEqual(post_count, Post.objects.all().count())
        self.assertEqual(post.text, form_data_edit['text'])
        self.assertEqual(post.group.id, form_data_edit['group'])
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.image, PATH_TO_IMAGE_EDIT)


class CommentFormTest(BaseTestCase):
    def test_authorized_user_comment_post(self):
        comment_count = Comment.objects.all().count()
        comment_data = {
            'text': 'Test comment',
            'post': self.posts,
            'author': self.author
        }
        response = self.authors_client.post(
            self.COMMENT_REVERSE,
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
        response = self.authors_client.get(
            self.POST_DETAIL_REVERSE)
        self.assertIn(created_comment, response.context['comments'])
