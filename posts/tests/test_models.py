from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Заголовок тестовой группы',
            description='Описание тестовой группы',
            slug='test-group',
        )
        cls.group = Group.objects.get(slug='test-group')

    def test_str(self):
        group = self.group
        expected_str = group.title
        self.assertEquals(expected_str, str(group))

    def test_verbose_name(self):
        group = self.group
        field_verboses = {
            'title': 'название группы',
            'description': 'описание группы',
            'slug': 'слэг',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

class PostModelTest(TestCase):
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

    def test_str(self):
        post = self.post
        expected_str = \
            f"{post.text[:15], post.pub_date, post.author, post.group}"
        self.assertEquals(expected_str, str(post))

    def test_verbose_name(self):
        post = self.post
        field_verboses = {
            'text': 'ваш пост',
            'pub_date': 'дата публикации',
            'author': 'автор поста',
            'group': 'группа поста',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = self.post
        field_help_texts = {
            'text': 'напишите свой пост здесь',
            'author': 'информация об авторе данного поста',
            'group': 'выберите группу из списка',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
