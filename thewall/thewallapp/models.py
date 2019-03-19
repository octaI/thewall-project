from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class Profile(AbstractUser):

    class Meta:
        ordering = ('id',)


class Comment(models.Model):
    posted = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50,blank=True)
    content = models.TextField()
    author_id = models.ForeignKey(Profile,blank=False, null=False,on_delete=models.CASCADE)
    comment_id= models.AutoField(primary_key=True)



    class Meta:
        ordering = ('posted',)
