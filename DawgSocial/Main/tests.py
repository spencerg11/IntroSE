from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import RegisterForm, PostForm, ShareForm
from .models import Post, Comment

class LoginTest(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code,200)

    def test_valid_login(self):
        response = self.client.post(reverse('login'), {'username': self.username,'password': self.password})
        self.assertEqual(response.status_code, 302)
        
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {'username': 'invalid_user','password':'invalid_password'})
        self.assertEqual(response.status_code, 200)

        self.assertFalse(response.wsgi_request.user.is_authenticated)


class RegisterTest(TestCase):
    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_valid_register(self):
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }

        response = self.client.post(reverse('register'),data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(response.wsgi_request.user.is_authenticated)

        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_invalid_register(self):
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'differentpassword',
        }

        response = self.client.post(reverse('register'),data)
        self.assertEqual(response.status_code, 200)

        self.assertFalse(response.wsgi_request.user.is_authenticated)

        self.assertFalse(User.objects.filter(username='testuser').exists())


class PostInteractionTest(TestCase):
    def setUp(self):
        # Creating a user and a sample post
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.post = Post.objects.create(user=self.user, content='This is a sample post.')

    def test_like_post(self):
        self.client.login(username=self.username, password=self.password)
        
        response = self.client.post(reverse('like_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)  

        self.assertTrue(self.post.liked_by.filter(id=self.user.id).exists())

    def test_comment_on_post(self):
        self.client.login(username=self.username, password=self.password)
        
        comment_text = 'Nice post!'
        response = self.client.post(reverse('post_comment', args=[self.post.id]), {'comment_text': comment_text})
        self.assertEqual(response.status_code, 302)  

        self.assertTrue(Comment.objects.filter(post=self.post, content=comment_text).exists())

    def test_repost_post(self):
        self.client.login(username=self.username, password=self.password)

        response = self.client.post(reverse('share_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)  

        self.assertTrue(Post.objects.filter(shared_user=self.user, content=self.post.content).exists())
