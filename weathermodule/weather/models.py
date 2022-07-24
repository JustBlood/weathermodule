from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models

class User(AbstractUser):
    pass

# class Users(models.Model):
#     first_name = models.CharField(max_length=60, null=False)
#     last_name = models.CharField(max_length=60, null=False)
#     login = models.CharField(max_length=30, null=False)
#     password = models.CharField(max_length=30, null=False)
#     stations = models.TextField()
#     stations_counter = models.IntegerField(validators=MaxValueValidator(1024))
#
# class Meteostations(models.Model):
#     name = models.CharField(max_length=50, null=False)
#     location = models.TextField()
#
# class Indicators(models.Model):
#     meteostation_id = models.ForeignKey('Meteostations', on_delete=models.CASCADE)
#     date = models.DateField()
#     time = models.TimeField()
#     uaccum = models.IntegerField()
#     photolight = models.IntegerField()
#     humground = models.IntegerField()
#     humair = models.FloatField()
#     tair = models.FloatField()
#     airpressure = models.FloatField()
#     tgroundsurface = models.FloatField()
#     tgrounddeep = models.FloatField()
#     wingspeed = models.FloatField()
#     wingdir = models.FloatField()