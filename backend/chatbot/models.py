from django.db import models

# Create your models here.
    
class conversation(models.Model):
    id = models.AutoField(primary_key=True)
    mbti = models.CharField(max_length=4, default='')
    #nick_id = models.ForeignKey('nickname', on_delete=models.CASCADE, db_column='nick_id')

    def __str__(self):
        return self.id
    
class UserMessage(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=200)
    #mbti = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    conv_id = models.ForeignKey('conversation', on_delete=models.CASCADE, db_column='conv_id')

    def __str__(self):
        return self.message, self.conv_id
    
class questions(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=20)
    question = models.CharField(max_length=100)

    def __str__(self):
        return self.question
    
class movie(models.Model):
    nfid = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    synopsis = models.CharField(max_length=500)
    review_key1 = models.CharField(max_length=20)
    review_key2 = models.CharField(max_length=20)
    review_key3 = models.CharField(max_length=20)
    movie_poster = models.CharField(max_length=200)

class recommendation(models.Model):
    id =  models.AutoField(primary_key=True)
    conv_id = models.ForeignKey('conversation', on_delete=models.CASCADE, db_column='conv_id')
    good = models.BooleanField()

class movie_recommendation(models.Model):
    id = models.AutoField(primary_key=True)
    nfid = models.ForeignKey(movie, on_delete=models.CASCADE, db_column='nfid')
    reco_id = models.ForeignKey(recommendation, on_delete=models.CASCADE, db_column='reco_id')




'''class Question(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField()

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField()'''


