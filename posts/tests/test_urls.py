from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from posts.models import Group, Post


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        site = Site.objects.get(pk=1)
        self.flat_about = FlatPage.objects.create(
            url='/contacts/',
            title='testtitle',
            content='<b>testcontent</b>'
        )
        self.flat_about.save()
        self.flat_about.sites.add(site)
        self.flat_author = FlatPage.objects.create(
            url='/about-author/',
            title='testtitle',
            content='<b>testcontent</b>'
        )
        self.flat_author.save()
        self.flat_author.sites.add(site)
        self.flat_spec = FlatPage.objects.create(
            url='/about-spec/',
            title='testtitle',
            content='<b>testcontent</b>'
        )
        self.flat_spec.save()
        self.flat_spec.sites.add(site)
        self.static_pages = ('/about-author/', '/about-spec/')

    def test_static_pages_response(self):
        for url in self.static_pages:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200, f'url: {url}')


class PostsURLTests(TestCase):
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
        cls.post = Post.objects.get(text='test post')
        Post.objects.create(
            text='test post 2',
            author=get_user_model().objects.create(
                username='testname2',
            ),
            group=Group.objects.create(
                title='testtitle2',
                description='testdescription2',
                slug='testslug2',
            ),
        )
        cls.post2 = Post.objects.get(text='test post 2')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.user = PostsURLTests.post.author
        self.authorized_client.force_login(self.user)
        self.user2 = PostsURLTests.post2.author
        self.authorized_client2.force_login(self.user2)

    def test_authorised_user_url_exists_at_desired_location_get(self):
        templates_response = {
            '': 200,
            '/group/testslug/': 200,
            '/new/': 200,
            '/testname/': 200,
            '/testname2/': 200,
            '/testname/1/': 200,
            '/testname2/2/': 200,
            '/testname/1/edit/': 200,
            '/testname2/2/edit/': 302,
        }
        for template, status_code in templates_response.items():
            with self.subTest():
                response = self.authorized_client.get(template)
                self.assertEqual(response.status_code, status_code)

    def test_authorised_user_url_exists_at_desired_location_post(self):
        templates_response = {
            '': 200,
            '/group/testslug/': 200,
            '/new/': 200,
            '/testname/': 200,
            '/testname2/': 200,
            '/testname/1/': 200,
            '/testname2/2/': 200,
            '/testname/1/edit/': 200,
            '/testname2/2/edit/': 302,
        }
        templates_response2 = {
            '/testname2/2/edit/': '/testname2/2/'
        }
        for template, status_code in templates_response.items():
            with self.subTest():
                response = self.authorized_client.post(template)
                self.assertEqual(response.status_code, status_code)
        for template, redirect_to in templates_response2.items():
            with self.subTest():
                response = self.authorized_client.post(template, follow=True)
                self.assertRedirects(response, redirect_to)

    def test_guest_url_exists_at_desired_location(self):
        templates_response1 = {
            '': 200,
            '/group/testslug/': 200,
            '/new/': 302,
            '/testname/': 200,
            '/testname/1/': 200,
            '/testname/1/edit/': 302,
            }
        templates_response2 = {
            '/new/': '/auth/signup/?new_post=/new/',
            '/testname/1/edit/': '/auth/login/?next=/testname/1/edit/'
        }
        for template, status_code in templates_response1.items():
            with self.subTest():
                response = self.guest_client.get(template)
                self.assertEqual(response.status_code, status_code)
        for template, redirect_to in templates_response2.items():
            with self.subTest():
                response = self.guest_client.get(template, follow=True)
                self.assertRedirects(response, redirect_to)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'index.html': '',
            'group.html': '/group/testslug/',
            'new_post.html': '/new/',
            'profile.html': '/testname/',
            'post.html': '/testname/1/',
        }
        templates_url_names2 = {
            'new_post.html': '/new/',
            'new_post.html': '/testname/1/edit/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        for template, reverse_name in templates_url_names2.items():
            with self.subTest():
                response = self.authorized_client.post(reverse_name)
                self.assertTemplateUsed(response, template)
