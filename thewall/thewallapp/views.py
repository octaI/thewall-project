# Create your views here.
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


class profile_detail_id(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Profile.objects.all()
    serializer_class = ProfileViewSerializer


class profile_detail(APIView):
    permission_classes = (
    permissions.IsAuthenticatedOrReadOnly, custompermissions.IsProfileOwner, custompermissions.IsSuperUser)

    def get_object(self, user_name):
        try:
            obj = Profile.objects.get(username=user_name)
            self.check_object_permissions(self.request, obj)
        except Profile.DoesNotExist:
            raise Http404
        return obj

    def get(self, request, user_name, format=None):
        profile = self.get_object(user_name)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_name, format=None):
        profile = self.get_object(user_name)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_name, format=None):
        profile = self.get_object(user_name)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class comment_list(generics.ListAPIView, generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            welcome_message = f'Hi {serializer.validated_data["username"]}! \n Welcome to The Wall!'
            mailing.send_emails('noreply@thewallapp.com', serializer.validated_data['email'], 'Welcome!',
                                welcome_message)
            profile = serializer.save()
            if profile:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


class profile_login(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            username = request.data['username']
            grant_type = request.data['grant_type']
            password = request.data['password']
            data = {'username': username,
                    'grant_type': grant_type,
                    'password': password,
                    'client_id': os.environ['CLIENT_ID'],
                    'client_secret': os.environ['CLIENT_SECRET']}
        except MultiValueDictKeyError:
            return Response({'detail': 'Badly built request. Required fields: username, grant_type, password'},
                            status=status.HTTP_400_BAD_REQUEST, content_type='application/json')
        if grant_type == 'refresh_token':
            try:
                data['refresh_token'] = request.data['refresh_token']
            except MultiValueDictKeyError:
                return Response({'detail': 'Missing refresh_token'}, status=status.HTTP_400_BAD_REQUEST)
        new_req = factory.post('/o/token.json', data)
        accestoken_view = TokenView.as_view()
        response = accestoken_view(new_req)
        return response
