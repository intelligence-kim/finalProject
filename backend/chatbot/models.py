from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=2)
    mbti = models.CharField(max_length=4)
    #email = models.EmailField()

    def __str__(self):
        return self.sex, self.mbti

class Message(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
    

