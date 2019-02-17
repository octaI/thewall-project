from django.test import TestCase
from .models import Comment, User
from rest_framework.test import APITestCase

# Create your tests here.

class CommentTests(TestCase):
    def setUp(self):
        User.objects.create(user_name='TestUser')
        comment_author = User.objects.get(user_name='TestUser')
        Comment.objects.create(title='Test', content='Test Content', author=comment_author)


    def test_comment_is_ok(self):

        comment = Comment.objects.get(title='Test')
        self.assertEqual(comment.title,'Test')
        self.assertEqual(comment.content,'Test Content')
