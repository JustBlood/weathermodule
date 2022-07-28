from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(
        _("email address"),
        unique=True,
    )

    # stations = models.TextField(default='')
    stations_counter = models.IntegerField(default=0, validators=[MaxValueValidator(1024),])
    email_verify = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


class UserMeteostations(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    meteostation = models.ForeignKey('Meteostations', on_delete=models.CASCADE)

class Meteostations(models.Model):
    pass

    def __lt__(self, other):
        return self.pk < other.pk

class Indicators(models.Model):
    meteostation_id = models.ForeignKey('Meteostations', on_delete=models.CASCADE)
    dt = models.DateTimeField()
    uaccum = models.IntegerField()
    photolight = models.IntegerField()
    humground = models.IntegerField()
    humair = models.FloatField()
    tair = models.FloatField()
    airpressure = models.FloatField()
    tgroundsurface = models.FloatField()
    tgrounddeep = models.FloatField()
    wingspeed = models.FloatField()
    wingdir = models.FloatField()