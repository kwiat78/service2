from django.db import models
from django.contrib.auth.models import User


class Track(models.Model):
    user = models.ForeignKey(User)
    label = models.CharField(max_length=256)
    processed = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)

    def __str__(self):
        return "{}-{}".format(self.user.username, self.label)


class Location(models.Model):
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    track = models.ForeignKey(Track, null=True)

    def __str__(self):
        return "{}-{}-({},{})".format(self.track.user.username, self.track.label,
                                      self.latitude, self.longitude)
