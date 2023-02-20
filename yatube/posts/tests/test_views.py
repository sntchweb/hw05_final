import shutil
import tempfile

from http import HTTPStatus

from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.forms import PostForm
from posts.models import Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

GROUP_SLUG = 'test_group'
TEST_USER = 'test_views1'
TEST_AUTHOR = 'test_post_author'
TEST_POST_TEXT = 'Test post text'
TEST_GROUP_TITLE = 'Test group title'
TEST_GROUP_DESCRIPTION = 'Test group description'
UNFOLLOWING_USER = 'unfollowing'
POST_PK = 1
POSTS_ON_FIRST_PAGE = 10
POSTS_ON_SECOND_PAGE = 3
TEST_POST_IMAGE = 'posts/small.gif'

INDEX_URL = reverse('posts:index')
GROUP_URL = reverse('posts:group_list', args=[GROUP_SLUG])
PROFILE_URL = reverse('posts:profile', args=[TEST_AUTHOR])
POST_DETAIL_URL = reverse('posts:post_detail', args=[POST_PK])
POST_CREATE_URL = reverse('posts:post_create')
POST_EDIT_URL = reverse('posts:post_edit', args=[POST_PK])
FOLLOW_URL = reverse('posts:profile_follow', args=[TEST_AUTHOR])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[TEST_AUTHOR])
FOLLOW_INDEX_URL = reverse('posts:follow_index')
SUBSCRIBE_URSELF = reverse('posts:profile_follow', args=[TEST_USER])

INDEX_TEMPLATE = 'posts/index.html'
GROUP_TEMPLATE = 'posts/group_list.html'
PROFILE_TEMPLATE = 'posts/profile.html'
POST_DETAIL_TEMPLATE = 'posts/post_detail.html'
POST_CREATE_TEMPLATE = 'posts/create_post.html'
POST_EDIT_TEMPLATE = 'posts/create_post.html'
FOLLOW_INDEX_TEMPLATE = 'posts/follow.html'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.ufollowing_user = User.objects.create_user(
            username=UNFOLLOWING_USER
        )
        cls.user = User.objects.create_user(username=TEST_USER)
        cls.post = Post.objects.create(
            author=User.objects.create_user(username=TEST_AUTHOR),
            text=TEST_POST_TEXT,
            group=Group.objects.create(
                title=TEST_GROUP_TITLE,
                slug=GROUP_SLUG),
            image=cls.uploaded_image
        )
        Post.objects.bulk_create([
            Post(
                text=TEST_POST_TEXT,
                author=cls.post.author,
                group=cls.post.group,
                image=cls.uploaded_image
            ) for i in range(POSTS_ON_FIRST_PAGE + 2)
        ])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.unfollowing_user = Client()
        self.unfollowing_user.force_login(self.ufollowing_user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_post_author = Client()
        self.authorized_post_author.force_login(self.post.author)
        cache.clear()

    def test_index_context(self):
        """Шаблон index/ сформирован с правильным контекстом."""
        response = self.authorized_client.get(INDEX_URL)
        context_object = response.context['page_obj'][0]
        self.assertEqual(context_object.text, self.post.text)
        self.assertEqual(context_object.group.title, self.post.group.title)
        self.assertEqual(
            context_object.author.username,
            self.post.author.username
        )
        self.assertTrue(
            Post.objects.filter(image=TEST_POST_IMAGE).exists()
        )

    def test_group_list_context(self):
        """Шаблон group_list/ сформирован с правильным контекстом."""
        response = self.authorized_client.get(GROUP_URL)
        context_object = response.context['page_obj'][0]
        context_object_group = response.context['group']
        self.assertEqual(context_object.text, self.post.text)
        self.assertEqual(context_object.group.title, self.post.group.title)
        self.assertEqual(context_object_group.title, self.post.group.title)
        self.assertEqual(context_object_group.slug, self.post.group.slug)
        self.assertTrue(
            Post.objects.filter(image=TEST_POST_IMAGE).exists()
        )

    def test_profile_context(self):
        """Шаблон profile/ сформирован с правильным контекстом."""
        response = self.authorized_client.get(PROFILE_URL)
        context_object = response.context['page_obj'][0]
        context_object_author = response.context['author']
        self.assertEqual(context_object.text, self.post.text)
        self.assertEqual(context_object.group.title, self.post.group.title)
        self.assertEqual(
            context_object.author.username,
            self.post.author.username
        )
        self.assertEqual(
            context_object_author.username,
            self.post.author.username
        )
        self.assertTrue(
            Post.objects.filter(image=TEST_POST_IMAGE).exists()
        )

    def test_post_detail_context(self):
        """Шаблон post_detail/ сформирован с правильным контекстом."""
        response = self.authorized_client.get(POST_DETAIL_URL)
        context_object = response.context['post']
        self.assertEqual(context_object.text, self.post.text)
        self.assertEqual(context_object.group.title, self.post.group.title)
        self.assertEqual(context_object.image, TEST_POST_IMAGE)
        self.assertEqual(
            context_object.author.username,
            self.post.author.username
        )

    def test_post_create_context(self):
        """Шаблон post_create/ сформирован с правильным контекстом."""
        response = self.authorized_client.get(POST_CREATE_URL)
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_edit_context(self):
        """Шаблон post_edit/ сформирован с правильным контекстом."""
        response = self.authorized_post_author.get(POST_EDIT_URL)
        context_object = response.context['is_edit']
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertTrue(context_object, True)

    def test_post_added_to_the_right_pages(self):
        """Добавленный пост отображается на страницах index/
        profile/ и group_list/ при указании группы.
        """
        urls_context = {
            INDEX_URL: ['page_obj'][0],
            GROUP_URL: 'group',
            PROFILE_URL: ['page_obj'][0],
        }
        for reverse_url, page_context in urls_context.items():
            with self.subTest(reverse_url=reverse_url):
                response = self.authorized_client.get(reverse_url)
                if page_context != 'group':
                    context_object = response.context[page_context][0]
                    self.assertEqual(context_object.text, self.post.text)
                    self.assertEqual(
                        context_object.group.title,
                        self.post.group.title
                    )
                    self.assertEqual(
                        context_object.author.username,
                        self.post.author.username
                    )
                else:
                    context_object = response.context[page_context]
                    self.assertEqual(
                        context_object.title,
                        self.post.group.title
                    )
                    self.assertEqual(
                        context_object.slug,
                        self.post.group.slug
                    )

    def test_first_and_second_page_contains_correct_count_of_records(self):
        """Количество постов на первой странице index/, group_list/
        и profile/ = 10, на второй = 3 . Страница доступна,
        у страницы нужный тип и != None."""
        pages = (
            (INDEX_URL, POSTS_ON_FIRST_PAGE),
            (GROUP_URL, POSTS_ON_FIRST_PAGE),
            (PROFILE_URL, POSTS_ON_FIRST_PAGE),
            (INDEX_URL + '?page=2', POSTS_ON_SECOND_PAGE),
            (GROUP_URL + '?page=2', POSTS_ON_SECOND_PAGE),
            (PROFILE_URL + '?page=2', POSTS_ON_SECOND_PAGE)
        )
        for url, posts_per_page in pages:
            response = self.client.get(url)
            page_obj = response.context.get('page_obj')
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIsNotNone(page_obj)
            self.assertIsInstance(page_obj, Page)
            self.assertEqual(len(response.context['page_obj']), posts_per_page)

    def test_cache_index_page(self):
        """Главная страница кешируется."""
        response1 = self.client.get(INDEX_URL + '?page=2')
        Post.objects.create(
            text=self.post.text,
            author=self.post.author,
        )
        response2 = self.client.get(INDEX_URL + '?page=2')
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.client.get(INDEX_URL + '?page=2')
        self.assertNotEqual(response1.content, response3.content)

    def test_authorized_user_can_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться на
        других пользователей и удалять их из подписок."""
        follower = User.objects.get(username=self.user)
        follows_count = follower.follower.all().count()
        self.authorized_client.get(FOLLOW_URL)
        self.assertEqual(follower.follower.all().count(), follows_count + 1)
        follows_before_unfollow = follower.follower.all().count()
        self.authorized_client.get(UNFOLLOW_URL)
        self.assertEqual(
            follower.follower.all().count(),
            follows_before_unfollow - 1
        )

    def test_new_post_on_followers_page(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        self.authorized_client.get(FOLLOW_URL)
        Post.objects.create(
            text=self.post.text,
            author=self.post.author,
        )
        response_new_post_in_feed = self.authorized_client.get(
            FOLLOW_INDEX_URL
        )
        new_post_in_context = response_new_post_in_feed.context['page_obj'][0]
        self.assertEqual(new_post_in_context.text, self.post.text)
        response_unfollow_user = self.unfollowing_user.get(
            FOLLOW_INDEX_URL
        )
        context_unfollowing = response_unfollow_user.context['page_obj']
        self.assertEqual(len(context_unfollowing), 0)

    def test_cannot_subscribe_urself(self):
        """Нельзя подписаться на самого себя."""
        follower = User.objects.get(username=self.user)
        followers_count = follower.follower.all().count()
        self.authorized_client.get(SUBSCRIBE_URSELF)
        self.assertEqual(followers_count, 0)
