from django.db import models
from django.contrib.auth.models import User


class Track(models.Model):
    user = models.ForeignKey(User)
    label = models.CharField(max_length=256)
    procesed = models.BooleanField(default=False)

    def __str__(self):
        return "{}-{}".format(self.user.username, self.label)


class Location(models.Model):
    user = models.ForeignKey(User)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    date = models.DateTimeField()
    label = models.CharField(max_length=256)
    track = models.ForeignKey(Track, null=True)

    def __str__(self):
        return "{}-{}-({},{})".format(self.user.username, self.label,
                                      self.latitude, self.longitude)
