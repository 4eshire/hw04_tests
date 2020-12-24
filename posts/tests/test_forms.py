import os
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.views import redirect_to_login
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


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
NAME2_GIF = 'small2.gif'
SMALL2_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
              b'\x01\x00\x80\x00\x00\x00\x00\x00'
              b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
              b'\x00\x00\x00\x2C\x00\x00\x00\x00'
              b'\x02\x00\x01\x00\x00\x02\x02\x0C'
              b'\x0A\x00\x3B'
              )
CONTENT_TYPE = 'image/gif'
NEW_POST_PAGE = reverse('new_post')


class PostFormTests(TestCase):
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
        self.user = self.post.author
        self.authorized_client.force_login(self.user)

    def test_create_post_from_guest(self):
        posts_count = Post.objects.count()
        url_create_post_from_guest = redirect_to_login(
            NEW_POST_PAGE, login_url='signup',
            redirect_field_name='new_post')['Location']
        uploaded = SimpleUploadedFile(
            name=NAME2_GIF,
            content=SMALL2_GIF,
            content_type=CONTENT_TYPE)
        with uploaded.open('rb') as image:
            form_data = {
                'text': TEXT2,
                'group': self.group2.id,
                #'image': image,
            }
            response = self.guest_client.post(
                NEW_POST_PAGE,
                format='multipart',
                data=form_data,
                follow=True
            )
        self.assertRedirects(response, url_create_post_from_guest)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(self.post, Post.objects.first())

    def test_create_post_from_authorized(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name=NAME2_GIF,
            content=SMALL2_GIF,
            content_type=CONTENT_TYPE)
        with uploaded.open('rb') as image:
            form_data = {
                'text': TEXT2,
                'group': self.group2.id,
                #'image': image,
            }
            response = self.authorized_client.post(
                NEW_POST_PAGE,
                format='multipart',
                data=form_data,
                follow=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        #self.assertEqual(uploaded.size, Post.objects.first().image.size)
        self.assertEqual(response.context.get('page')[0].author,
                         Post.objects.first().author)
        self.assertEqual(response.context.get('page')[0].text,
                         Post.objects.first().text)
        self.assertEqual(response.context.get('page')[0].group,
                         Post.objects.first().group)

    def test_edit_post_from_guest(self):
        posts_count = Post.objects.count()
        edit_post_from_guest_url = redirect_to_login(
            reverse('post_edit',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk,}),
            login_url='login')['Location']
        uploaded = SimpleUploadedFile(
            name=NAME2_GIF,
            content=SMALL2_GIF,
            content_type=CONTENT_TYPE)
        with uploaded.open('rb') as image:
            form_data = {
                'text': TEXT2,
                'group': self.group2.id,
                #'image': image,
            }
            response = self.guest_client.post(
                reverse('post_edit', kwargs={
                    'username': self.post.author.username,
                    'post_id': self.post.pk,}),
                data=form_data,
                follow=True
            )
        self.assertRedirects(response, edit_post_from_guest_url)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(self.post, Post.objects.first())

    def test_edit_post_from_authorized_author(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name=NAME2_GIF,
            content=SMALL2_GIF,
            content_type=CONTENT_TYPE)
        with uploaded.open('rb') as image:
            form_data = {
                'text': TEXT2,
                'group': self.group2.id,
                #'image': image,
            }
            response = self.authorized_client.post(
                reverse('post_edit', kwargs={
                    'username': self.post.author.username,
                    'post_id': self.post.pk,}),
                data=form_data,
                follow=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), posts_count)
        #self.assertEqual(uploaded.size, Post.objects.first().image.size)
        self.assertEqual(response.context.get('post').author,
                         Post.objects.first().author)
        self.assertEqual(response.context.get('post').text,
                         Post.objects.first().text)
        self.assertEqual(response.context.get('post').group,
                         Post.objects.first().group)
