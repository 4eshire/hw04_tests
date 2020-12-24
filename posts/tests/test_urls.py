import os
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.flatpages import views
from django.contrib.auth.views import redirect_to_login
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, SimpleTestCase, override_settings
from django.urls import reverse, resolve, Resolver404

from posts.models import Group, Post, User
from posts.views import page_not_found
from yatube import settings

ABOUT_URL = '/contacts/'
ABOUT_AUTHOR_URL = reverse('about-author')
ABOUT_SPEC_URL = reverse('about-spec')
FLATPAGE_TITLE = 'testtitle'
FLATPAGE_CONTENT = '<b>testcontent</b>'
TEXT = 'test post'
USERNAME = 'testname'
TITLE = 'testtitle'
DESCRIPTION = 'testdescription'
SLUG = 'testslug'
TEXT2 = 'new post'
USERNAME2 = 'testname2'
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
INDEX_PAGE = reverse('index')
GROUP_PAGE = reverse('group_posts', kwargs={'slug': SLUG})
NEW_POST_PAGE = reverse('new_post')
PROFILE_PAGE = reverse('profile', kwargs={'username': USERNAME})
PROFILE_PAGE2 = reverse('profile', kwargs={'username': USERNAME2})

class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        site = Site.objects.get(pk=1)
        self.flat_about = FlatPage.objects.create(
            url=ABOUT_URL,
            title=FLATPAGE_TITLE,
            content=FLATPAGE_CONTENT
        )
        self.flat_about.save()
        self.flat_about.sites.add(site)
        self.flat_author = FlatPage.objects.create(
            url=ABOUT_AUTHOR_URL,
            title=FLATPAGE_TITLE,
            content=FLATPAGE_CONTENT
        )
        self.flat_author.save()
        self.flat_author.sites.add(site)
        self.flat_spec = FlatPage.objects.create(
            url=ABOUT_SPEC_URL,
            title=FLATPAGE_TITLE,
            content=FLATPAGE_CONTENT
        )
        self.flat_spec.save()
        self.flat_spec.sites.add(site)
        self.static_pages = (ABOUT_AUTHOR_URL, ABOUT_SPEC_URL)

    def test_static_pages_response(self):
        for url in self.static_pages:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200, f'url: {url}')


class PostsURLTests(TestCase):
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
        cls.post2 = Post.objects.create(
            text=TEXT2,
            author=User.objects.create(
                username=USERNAME2,
            ),
            group=Group.objects.create(
                title=TITLE2,
                description=DESCRIPTION2,
                slug=SLUG2,
            ),
            #image=SimpleUploadedFile(
            #    name=NAME2_GIF,
            #    content=SMALL2_GIF,
            #    content_type=CONTENT_TYPE
            #),
        )
        cls.post_page = reverse('post', kwargs={
            'username': cls.post.author.username,
            'post_id': cls.post.pk
        })
        cls.post2_page = reverse('post', kwargs={
            'username': cls.post2.author.username,
            'post_id': cls.post2.pk
        })
        cls.post_edit_page = reverse('post_edit', kwargs={
            'username': cls.post.author.username,
            'post_id': cls.post.pk,
        })
        cls.post2_edit_page = reverse('post_edit', kwargs={
            'username': cls.post2.author.username,
            'post_id': cls.post2.pk,
        })

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.user = PostsURLTests.post.author
        self.authorized_client.force_login(self.user)
        self.user2 = PostsURLTests.post2.author
        self.authorized_client2.force_login(self.user2)

    def test_user_url_exists_at_desired_location(self):
        url_response = {
            INDEX_PAGE: [200, 200, 200],
            GROUP_PAGE: [200, 200, 200],
            NEW_POST_PAGE: [200, 200, 302],
            PROFILE_PAGE: [200, 200, 200],
            PROFILE_PAGE2: [200, 200, 200],
            self.post_page: [200, 200, 200],
            self.post2_page: [200, 200, 200],
            self.post_edit_page: [200, 200, 302],
            self.post2_edit_page: [302, 302, 302],
        }
        for url, status_codes in url_response.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                response2 = self.authorized_client.post(url)
                response3 = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_codes[0])
                self.assertEqual(response2.status_code, status_codes[1])
                self.assertEqual(response3.status_code, status_codes[2])

    def test_user_url_redirect_to(self):
        url_create_post_from_guest = redirect_to_login(
            NEW_POST_PAGE, login_url='signup',
            redirect_field_name='new_post')['Location']
        edit_post_from_guest_url = redirect_to_login(
            reverse('post_edit',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk, }),
            login_url='login')['Location']
        url_response = {
            self.post2_edit_page: [self.post2_page, 'post'],
            NEW_POST_PAGE: [url_create_post_from_guest, 'get'],
            self.post_edit_page: [edit_post_from_guest_url, 'get'],
        }
        for url, redirect_to in url_response.items():
            with self.subTest():
                if redirect_to[1] == 'post':
                    response = self.authorized_client.post(url, follow=True)
                    self.assertRedirects(response, redirect_to[0])
                elif redirect_to[1] == 'get':
                    response = self.guest_client.get(url, follow=True)
                    self.assertRedirects(response, redirect_to[0])

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            (INDEX_PAGE, 'get'): 'index.html',
            (GROUP_PAGE, 'get'): 'group.html',
            (PROFILE_PAGE, 'get'):  'profile.html',
            (self.post_page, 'get'): 'post.html',
            (NEW_POST_PAGE, 'post'): 'new_post.html',
            (self.post_edit_page, 'post'): 'new_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest():
                if url[1] == 'post':
                    response = self.authorized_client.post(url[0])
                    self.assertTemplateUsed(response, template)
                elif url[1] == 'get':
                    response = self.guest_client.get(url[0])
                    self.assertTemplateUsed(response, template)
