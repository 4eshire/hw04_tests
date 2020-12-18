from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, SimpleTestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post
from posts.views import page_not_found


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            text='test post',
            author=get_user_model().objects.create(
                username='testname',
            ),
            group=Group.objects.create(
                title='testtitle',
                description='testdescription',
                slug='testslug',
            ),
        )
        cls.post = Post.objects.get()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = PostsPagesTests.post.author
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': (reverse('group_posts',
                                   kwargs={'slug': 'testslug'})),
            'new_post.html': reverse('new_post'),
            'profile.html': (reverse('profile',
                                     kwargs={'username': 'testname'})),
            'post.html': (
                reverse('post', kwargs={'username': 'testname', 'post_id': 1})
            ),
        }
        templates_pages_names2 = {
            'new_post.html': reverse('new_post'),
            'new_post.html': (
                reverse('post_edit',
                        kwargs={'username': 'testname', 'post_id': 1})),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        for template, reverse_name in templates_pages_names2.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.post(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        index_text_0 = response.context.get('page')[0].text
        index_author_0 = response.context.get('page')[0].author
        index_group_0 = response.context.get('page')[0].group
        self.assertEqual(index_text_0, 'test post')
        self.assertEqual(index_author_0, self.post.author)
        self.assertEqual(index_group_0, self.post.group)

    def test_group_pages_show_correct_context(self):
        response = self.authorized_client.get(
                reverse('group_posts', kwargs={'slug': 'testslug'})
        )
        group_text_0 = response.context.get('page')[0].text
        group_author_0 = response.context.get('page')[0].author
        group_group_0 = response.context.get('page')[0].group
        title_group_0 = response.context.get('page')[0].group.title
        slug_group_0 = response.context.get('page')[0].group.slug
        desc_group_0 = response.context.get('page')[0].group.description
        self.assertEqual(group_text_0, 'test post')
        self.assertEqual(group_author_0, self.post.author)
        self.assertEqual(group_group_0, self.post.group)
        self.assertEqual(title_group_0, 'testtitle')
        self.assertEqual(slug_group_0, 'testslug')
        self.assertEqual(desc_group_0, 'testdescription')

    def test_new_post_pages_show_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_pages_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'profile', kwargs={'username': 'testname'}))
        group_text_0 = response.context.get('page')[0].text
        group_author_0 = response.context.get('page')[0].author
        group_group_0 = response.context.get('page')[0].group
        title_group_0 = response.context.get('page')[0].group.title
        slug_group_0 = response.context.get('page')[0].group.slug
        desc_group_0 = response.context.get('page')[0].group.description
        self.assertEqual(group_text_0, 'test post')
        self.assertEqual(group_author_0, self.post.author)
        self.assertEqual(group_group_0, self.post.group)
        self.assertEqual(title_group_0, 'testtitle')
        self.assertEqual(slug_group_0, 'testslug')
        self.assertEqual(desc_group_0, 'testdescription')

    def test_post_pages_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'post', kwargs={'username': 'testname', 'post_id': 1}))
        group_text_0 = response.context.get('page')[0].text
        group_author_0 = response.context.get('page')[0].author
        group_group_0 = response.context.get('page')[0].group
        title_group_0 = response.context.get('page')[0].group.title
        slug_group_0 = response.context.get('page')[0].group.slug
        desc_group_0 = response.context.get('page')[0].group.description
        self.assertEqual(group_text_0, 'test post')
        self.assertEqual(group_author_0, self.post.author)
        self.assertEqual(group_group_0, self.post.group)
        self.assertEqual(title_group_0, 'testtitle')
        self.assertEqual(slug_group_0, 'testslug')
        self.assertEqual(desc_group_0, 'testdescription')

    def test_post_edit_pages_show_correct_context(self):
        response = self.authorized_client.post(reverse(
            'post_edit', kwargs={'username': 'testname', 'post_id': 1}))
        form_fields = {
            "user_profile",
            "form"
        }
        for expected in form_fields:
            with self.subTest():
                self.assertIn(expected, response.context)

    def test_handler_renders_template_response(self):
        response = self.guest_client.get('404/')
        self.assertTemplateUsed(response, 'misc/404.html')
        self.assertEqual(response.status_code, 404)
