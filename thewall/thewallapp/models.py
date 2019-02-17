from django.contrib.postgres.forms import JSONField
from django.db import models

# Create your models here.

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=30)


class Comment(models.Model):
    posted = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    content = models.TextField()
    author = models.ForeignKey(User,blank=False, null=False,on_delete=models.CASCADE)
    comment_id= models.AutoField(primary_key=True)



    class Meta:
        ordering = ('posted',)
