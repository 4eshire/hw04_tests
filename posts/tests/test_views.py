import os
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, SimpleTestCase, override_settings
from django.urls import reverse, resolve, Resolver404

from posts.models import Group, Post, User
from posts.views import page_not_found
from yatube import settings


TEXT = 'test post'
USERNAME = 'testname'
TITLE = 'testtitle'
DESCRIPTION = 'testdescription'
SLUG = 'testslug'
TEXT2 = 'new post'
TITLE2 = 'testtitle2'
DESCRIPTION2 = 'testdescription2'
SLUG2 = 'testslug2'
NAME_GIF = 'small.gif'
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
             )
CONTENT_TYPE = 'image/gif'
INDEX_PAGE = reverse('index')
GROUP_PAGE = reverse('group_posts', kwargs={'slug': SLUG})
NEW_POST_PAGE = reverse('new_post')
PROFILE_PAGE = reverse('profile', kwargs={'username': USERNAME})


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.post = Post.objects.create(
            text=TEXT,
            author=User.objects.create(
                username=USERNAME,
            ),
            group=Group.objects.create(
                title=TITLE,
                description=DESCRIPTION,
                slug=SLUG,
            ),
            #image=SimpleUploadedFile(
            #    name=NAME_GIF,
            #    content=SMALL_GIF,
            #    content_type=CONTENT_TYPE
            #),
        )
        cls.group2 = Group.objects.create(
            title=TITLE2,
            description=DESCRIPTION2,
            slug=SLUG2,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = PostsPagesTests.post.author
        self.authorized_client.force_login(self.user)

    def test_page_show_correct_context(self):
        test_page_params = {
            INDEX_PAGE: {'none': None},
            GROUP_PAGE: {'group': Group.objects.get(slug=SLUG)},
            PROFILE_PAGE: {'author': User.objects.get(username=USERNAME)},
        }
        for reverse_name, assert_params in test_page_params.items():
            for get_data, expected in assert_params.items():
                with self.subTest():
                    response = self.authorized_client.get(reverse_name)
                    self.assertEqual(response.context.get(get_data), expected)
                    self.assertEqual(
                        response.context.get('page')[0], self.post
                    )

    def test_post_pages_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'post', kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk})
        )
        show_post = response.context.get('post')
        self.assertEqual(show_post, self.post)

    def test_new_post_pages_show_correct_context(self):
        response = self.authorized_client.get(NEW_POST_PAGE)
        form_fields = {
            'text': forms.CharField,
            'group': forms.ModelChoiceField,
            #'image': forms.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_pages_show_correct_context(self):
        response = self.authorized_client.post(reverse(
            'post_edit', kwargs={
                'username': self.post.author.username,
                'post_id': self.post.pk,
            })
        )
        form_fields = {
            "author",
            "form"
        }
        for expected in form_fields:
            with self.subTest():
                self.assertIn(expected, response.context)

    def test_handler_renders_template_response(self):
        response = self.guest_client.get('404/')
        self.assertEqual(response.status_code, 404)


class TestError404(TestCase):
    def setUp(self):
        self.client = Client()
        self.debug = settings.DEBUG
        settings.DEBUG = False

    def tearDown(self):
        settings.DEBUG = self.debug

    def test_404(self):
        with self.assertRaises(Resolver404):
            resolve(page_not_found)
