from rest_framework import serializers
from .models import Comment,Profile


class CommentSerializer(serializers.Serializer):
    posted=serializers.DateTimeField()
    title=serializers.CharField()
    content=serializers.CharField()
    author=serializers.IntegerField(read_only=True)
    comment_id=serializers.IntegerField()

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title',instance.title)
        instance.content = validated_data.get('content',instance.content)
        instance.save()
        return instance

class ProfileSerializer(serializers.Serializer):
    user_id= serializers.IntegerField()
    user_name= serializers.CharField()
    email= serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    registration_date= serializers.DateField()


    def create(self, validated_data):
        return Profile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.user_name = validated_data.get('user_name',instance.user_name)
        instance.email = validated_data.get('email',instance.email)
        instance.first_name = validated_data.get('first_name',)
        instance.save()
