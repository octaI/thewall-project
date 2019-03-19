import os

from oauth2_provider.settings import oauth2_settings
from oauth2_provider.models import get_access_token_model,get_application_model


from django.test import TestCase
from django.contrib.auth.hashers import make_password

from .models import Comment, Profile
from rest_framework.test import APIClient
from rest_framework import status

# Create your tests here.

client = APIClient()
Application = get_application_model()
AccessToken = get_access_token_model()


class CommentTests(TestCase):
    def setUp(self):
        self.comment_author = Profile.objects.create(username='TestUser',email='test@test.xxx',password='supersecret1')
        self.comment = Comment.objects.create(title='Test', content='Test Content', author_id=self.comment_author)

    def test_comment_is_ok(self):

        comment = Comment.objects.get(comment_id = self.comment.comment_id)
        self.assertEqual(comment.title,'Test')
        self.assertEqual(comment.content,'Test Content')
        self.assertEqual(comment.author_id.id,self.comment_author.id)

    def tearDown(self):
        self.comment.delete()
        self.comment_author.delete()





class ApiTests(TestCase):
    def setUp(self):
        self.user1 = Profile.objects.create(username='TestUser1',email='test1@test.com',password=make_password('supersecret1'))
        self.user2 = Profile.objects.create(username='TestUser2',email='test2@test.com',password=make_password('supersecret2'))
        self.super_user = Profile.objects.create(username='SuperAdminTest',email='iamadmin@test.com',password=make_password('supersecretadmin1'),is_superuser=True)

        self.comment = Comment.objects.create(title='Test',content='Test Content1',author_id=self.user1)

        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.user1,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        self.application.save()
        oauth2_settings._SCOPES = ['read', 'write']

        os.environ['CLIENT_ID'] = self.application.client_id
        os.environ['CLIENT_SECRET'] = self.application.client_secret

    def tearDown(self):
        self.application.delete()
        self.comment.delete()
        self.user1.delete()
        self.user2.delete()


    def test_get_comments_unauthed(self):
        response = client.get('/comments/')
        json_resp = response.json()
        self.assertEqual(len(json_resp),1)
        self.assertEqual(json_resp[0]['content'],self.comment.content)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_post_comment_unauthed(self):
        response = client.post('/comments/',{'title': 'Test Unauthed', 'content': 'Trying to post unauthed',
                                             'author_id': self.user1.id})
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_post_comment_authed(self):
        client.force_authenticate(self.user1)
        data = {
            'title' : 'Test Auth Comment',
            'content': 'This should work',
            'author_id': self.user1.id
        }
        response = client.post('/comments/',data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.json()['content'],data['content'])
        client.force_authenticate(user=None)

    def test_post_comment_authed_impersonate(self):
        client.force_authenticate(self.user1)
        data = {
            'title': 'I want to be someone else',
            'content': 'This is naughty',
            'author_id': self.user1.id+1
        }
        response = client.post('/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        client.force_authenticate(user=None)

    def test_failed_login(self):
        response = client.post('/login/',{'username': 'TestUser1','password':'wrongpass','grant_type': 'password'})
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_bad_login_request(self):
        response = client.post('/login/',{'username': 'TestUser1','password':'wrongpass','grant_type': 'wrong'})
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        response = client.post('/login/',{'username': 'TestUser1','password':'wrongpass'})
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
    def test_successful_login(self):
        response = client.post('/login/',
                               {'username': 'TestUser1', 'password': 'supersecret1', 'grant_type': 'password',
                                'client_id': os.environ['CLIENT_ID'],
                                'client_secret': os.environ['CLIENT_SECRET']})
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertIsNotNone(response.json()['access_token'])
        self.assertIsNotNone(response.json()['refresh_token'])
        response = client.post('/login/',
                               {'username': 'testuser1', 'password': 'supersecret1', 'grant_type': 'password',
                                'client_id': os.environ['CLIENT_ID'],
                                'client_secret': os.environ['CLIENT_SECRET']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json()['access_token'])
        self.assertIsNotNone(response.json()['refresh_token'])
    def test_successful_token_refresh(self):
        response = client.post('/login/',{'username': 'TestUser1','password':'supersecret1','grant_type': 'password','client_id': self.application.client_id,
                                           'client_secret': self.application.client_secret})
        refresh_token = response.json()['refresh_token']
        access_token = response.json()['access_token']
        response_2 = client.post('/login/',{'username': 'TestUser1','password':'supersecret1','grant_type': 'refresh_token',
                                          'refresh_token': refresh_token})
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertNotEqual(refresh_token,response_2.json()['refresh_token'])
        self.assertNotEqual(access_token,response_2.json()['access_token'])

    def test_successful_registration(self):
        data = {
            'username': 'RegisteredTest',
            'password': 'supersecret3',
            'email': 'registertest@test.com'
        }

        response = client.post('/register/',data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.json()['username'],data['username'])
        self.assertEqual(response.json()['email'],data['email'])

    def test_duplicated_registration(self):
        data = {
            'username': 'TestUser1',
            'password': 'supersecret3',
            'email': 'registertest@test.com'
        }
        response = client.post('/register/',data)
        self.assertEqual(response.status_code,status.HTTP_406_NOT_ACCEPTABLE)

    def test_duplicated_registration_case_insensitive(self):
        data = {
            'username': 'testuser1',
            'password': 'supersecret3',
            'email': 'registertest@test.com'
        }
        response = client.post('/register/',data)
        self.assertEqual(response.status_code,status.HTTP_406_NOT_ACCEPTABLE)

    def test_user_modify_anotheruser_notsuperadmin(self):
        client.force_authenticate(user=self.user2)
        data = {
            'username': 'NaughtyUser',
            'password': 'notmypass',
            'email': 'icantdothat@test.com'
        }
        response = client.put('/profile/'+str(self.user1.id),data)
        client.force_authenticate(user=None)
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_user_modify_onefield(self):
        client.force_authenticate(user=self.user2)
        newname = 'GoodUser'
        data = {
            'username': newname,
        }
        response = client.put('/profile/' + str(self.user2.id), data)
        new_profile = Profile.objects.get(pk=self.user2.id)
        client.force_authenticate(user=None)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(new_profile.username, newname)


    def test_user_delete_anotheruser_notsuperadmin(self):
        client.force_authenticate(user=self.user2)

        response = client.delete('/profile/'+str(self.user1.id))
        client.force_authenticate(user=None)
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_user_modify_itself(self):
        client.force_authenticate(user=self.user2)
        newname = 'GoodUser'
        data = {
            'username': newname,
            'email': 'icandothat@test.com'
        }
        response = client.put('/profile/' + str(self.user2.id), data)
        new_profile = Profile.objects.get(pk=self.user2.id)
        client.force_authenticate(user=None)
        self.assertEqual(response.status_code,status.HTTP_202_ACCEPTED)
        self.assertEqual(new_profile.username,newname)

    def test_user_delete_itself(self):
        client.force_authenticate(user=self.user2)
        response = client.delete('/profile/' + str(self.user2.id))
        client.force_authenticate(user=None)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_superuser_modify_anotheruser(self):
        client.force_authenticate(user=self.super_user)
        data = {
            'username': 'NaughtyAdmin',
            'password': 'changedhispass',
            'email': 'icandothat@test.com'
        }
        response = client.put('/profile/' + str(self.user1.id), data)
        client.force_authenticate(user=None)
        modified_user1 = Profile.objects.get(pk=self.user1.id)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(modified_user1.username,'NaughtyAdmin')

    def test_anon_tries_superuser(self):
        data = {
            'username': 'HackyAnon',
            'password': 'supersecret3',
            'email': 'registerbadsuperusertest@test.com',
            'is_superuser': True
        }

        response = client.post('/register/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


