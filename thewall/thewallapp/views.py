# Create your views here.
from django.conf import settings
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.response import Response
from . import mailing
import json, os

from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from oauth2_provider.views import TokenView

from .models import Profile, Comment
from .serializers import ProfileSerializer, CommentSerializer, ProfileViewSerializer
from . import custompermissions

factory = APIRequestFactory() #DRF request factorya


class profile_list(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profile.objects.all()
    serializer_class = ProfileViewSerializer


class username_unique(APIView):
    permission_classes=(permissions.AllowAny,)
    def get(self,request):
        username = self.request.query_params.get('username')
        obj = Profile.objects.filter(username__iexact=username)
        if not obj.exists():
            return Response(status=status.HTTP_200_OK)
        return Response({'detail': 'Username already exists'},status=status.HTTP_406_NOT_ACCEPTABLE)





class profile_detail(APIView):
    permission_classes = (
    permissions.IsAuthenticated, custompermissions.IsProfileOwner, custompermissions.IsSuperUser)

    def get_object(self, user_id):
        try:
            obj = Profile.objects.get(pk=user_id)
            self.check_object_permissions(self.request, obj)
        except Profile.DoesNotExist:
            raise Http404
        return obj

    def get(self, request, user_id, format=None):
        profile = self.get_object(user_id)
        serializer = ProfileViewSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id, format=None):
        profile = self.get_object(user_id)
        serializer = ProfileViewSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, format=None):
        profile = self.get_object(user_id)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class comment_list(generics.ListAPIView,generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, custompermissions.IsRealAuthor)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class comment_detail(APIView):
    permission_classes = (
    permissions.IsAuthenticatedOrReadOnly, custompermissions.IsProfileOwner, custompermissions.IsSuperUser)

    def get_object(self, request, comment_id):
        try:
            obj = Comment.objects.get(comment_id=comment_id)
            return obj
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, comment_id):
        comment = self.get_object(request, comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def delete(self, request, comment_id):
        comment = self.get_object(request, comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class profile_create(APIView):
    permission_classes = (permissions.AllowAny,custompermissions.AnonTriesToSuperUser)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            if settings.DEBUG == False: #don't send emails when testing
                welcome_message = f'Hi {serializer.validated_data["username"]}! \n Welcome to The Wall!'
                mailing.send_emails('noreply@thewallapp.com', serializer.validated_data['email'], 'Welcome to The Wall!',
                                    welcome_message)
            profile = serializer.save()
            return_data = serializer.data
            del return_data['password']
            if profile:
                return Response(return_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


class profile_login(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            grant_type = request.data['grant_type']
        except MultiValueDictKeyError:
            return Response({'detail': 'Badly built request. grant_type field required'},
                            status=status.HTTP_400_BAD_REQUEST,content_type='application/json')

        data = {'grant_type': grant_type,
                'client_id': os.environ['CLIENT_ID'],
                'client_secret': os.environ['CLIENT_SECRET']}

        if (grant_type == 'password'):
            try:
                username = request.data['username']
                password = request.data['password']
            except MultiValueDictKeyError:
                return Response({'detail': 'Badly built request. Required fields: username, password'},
                                status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
            try:
                user_data = Profile.objects.get(username__iexact=username) #get the user data
            except Profile.DoesNotExist:
                return Response({'detail': f'Username {username} does not exist'}, status=status.HTTP_404_NOT_FOUND,content_type='application/json')
            data = {**data, 'username': user_data.username, 'password': password}

        if grant_type == 'refresh_token':
            try:
                data['refresh_token'] = request.data['refresh_token']
            except MultiValueDictKeyError:
                return Response({'detail': 'Missing refresh_token'}, status=status.HTTP_400_BAD_REQUEST)
        new_req = factory.post('/o/token.json', data)
        accestoken_view = TokenView.as_view()
        response = accestoken_view(new_req)
        if (response.status_code == status.HTTP_200_OK and grant_type=='password'): #append user_data on first login
            user_dict = {'user_data': {'id': user_data.id,'username': user_data.username,'email': user_data.email,
                                       'first_name': user_data.first_name,'last_name': user_data.last_name}}
            response.content = json.dumps({**json.loads(response.content),**user_dict})
        return response
