from django.db import models
from django.contrib.auth.models import User


class Location(models.Model):
    user = models.ForeignKey(User)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    date = models.DateTimeField()
    label = models.CharField(max_length=100)

    def __str__(self):
        return "{}-{}-({},{})".format(self.user.username, self.label,
                                      self.latitude, self.longitude)

