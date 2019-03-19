from rest_framework import serializers

from .models import Comment, Profile

def check_unique_username(attrs,errors):
    unique_username = Profile.objects.filter(username__iexact=attrs['username'])
    if (unique_username.exists()):
        errors['username'] = 'Field must be unique'

def check_unique_email(attrs,errors):
    unique_email = Profile.objects.filter(email__iexact=attrs['email'])
    if (unique_email.exists()):
        errors['email'] = 'Field must be unique'


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author_id.username')
    content = serializers.CharField(min_length=10)
    title = serializers.CharField(min_length=8)

    class Meta:
        model = Comment
        fields = ['posted', 'title', 'content', 'author_id', 'author_name', 'comment_id']


class ProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

    def validate(self, attrs):
        errors = {}
        if 'username' in attrs:
            check_unique_username(attrs,errors)
        if 'email' in attrs:
            check_unique_email(attrs,errors)

        if errors:
            raise serializers.ValidationError(errors)
        return attrs



class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True,min_length=8, max_length=150,
                                     )
    password = serializers.CharField(min_length=8)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']

    def validate(self, attrs):
        errors = {}
        check_unique_username(attrs,errors)
        check_unique_email(attrs,errors)
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

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
