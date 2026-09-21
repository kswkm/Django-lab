from django.db import models

class Score1(models.Model):
    myname1 = models.CharField(max_length=100)
    score1 = models.IntegerField()

    def __str__(self):
        return self.myname1

# Create your models here.
