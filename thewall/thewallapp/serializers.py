from rest_framework import serializers
from .models import Comment,Profile
from rest_framework.validators import UniqueValidator



class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author_id.username')
    class Meta:
        model = Comment
        fields = ['posted', 'title', 'content', 'author_id','author_name', 'comment_id']

class ProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id','username','email','first_name','last_name']


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=Profile.objects.all())])
    username = serializers.CharField(required=True,max_length=150,validators=[UniqueValidator(queryset=Profile.objects.all())])
    password = serializers.CharField(min_length=8)


    class Meta:
        model = Profile
        fields = ['id','username','email','first_name','last_name','password']


    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance