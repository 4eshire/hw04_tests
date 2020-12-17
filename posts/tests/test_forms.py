from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post


class PostFormTests(TestCase):
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
        self.user = PostFormTests.post.author
        self.authorized_client.force_login(self.user)

    def test_create_post_from_guest(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'new post',
            'author': 'new author',
            'group': 'new group',
        }
        response = self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/signup/?new_post=/new/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_post_from_authorized(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'new post',
            'group': '',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), posts_count+1)

    def test_edit_post_from_guest(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'new post2',
            'author': 'new author2',
            'group': 'new group2',
        }
        response = self.guest_client.post(
            reverse('post_edit', kwargs={
                'username': 'testname', 'post_id': 1,}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/testname/1/edit/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post_from_guest(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'new post2',
            'group': 'new group2',
        }
        response = self.guest_client.post(
            reverse('post_edit', kwargs={
                'username': 'testname', 'post_id': 1,}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/testname/1/edit/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post_from_authorized_author(self):
        posts_count = Post.objects.count()
        form_data = {
        'text': 'new post2',
        'group': 'new group2',
        }
        response = self.authorized_client.post(reverse('post_edit', kwargs={
            'username': 'testname', 'post_id': 1, }),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), posts_count)
