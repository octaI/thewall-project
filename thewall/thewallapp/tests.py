from django.test import TestCase
from .models import Comment, Profile
from rest_framework.test import APITestCase

# Create your tests here.

class CommentTests(TestCase):
    def setUp(self):
        Profile.objects.create(user_name='TestUser',email='test@test.xxx')
        comment_author = Profile.objects.get(user_name='TestUser',email='test@test.xxx')
        Comment.objects.create(title='Test', content='Test Content', author=comment_author)


    def test_comment_is_ok(self):

        comment = Comment.objects.get(title='Test')
        self.assertEqual(comment.title,'Test')
        self.assertEqual(comment.content,'Test Content')
