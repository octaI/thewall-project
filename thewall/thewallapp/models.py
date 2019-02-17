from django.contrib.postgres.forms import JSONField
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

# Create your models here.

class Profile(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=30,unique=True, null=False)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True,null=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    registration_date = models.DateField(auto_now_add=True)

    USERNAME_FIELD = 'user_name'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name', 'email']

    class Meta:
        ordering = ('user_id', )


class Comment(models.Model):
    posted = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    content = models.TextField()
    author = models.ForeignKey(Profile,blank=False, null=False,on_delete=models.CASCADE)
    comment_id= models.AutoField(primary_key=True)



    class Meta:
        ordering = ('posted',)
