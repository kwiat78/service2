from django.db import models
from django.contrib.auth.models import User


class Feed(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    postLimit = models.IntegerField(default=20)
    favIcon = models.CharField(max_length=511)
    position = models.IntegerField()

    def __str__(self):
        return "{}'s {}".format(self.user.username, self.name)


class Link(models.Model):
    url = models.CharField(max_length=511)

    def __str__(self):
        return self.url


class FeedLink(models.Model):
    link = models.ForeignKey(Link)
    feed = models.ForeignKey(Feed, related_name="links")
    reg_exp = models.CharField(max_length=511, blank=True, null=True)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ('position',)

    def __str__(self):
        return "{}'s {}".format(self.feed, self.link.url)


class Post(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=511)
    post_date = models.DateTimeField()
    add_date = models.DateTimeField()
    view = models.BooleanField()
    seen = models.BooleanField(default=True)
    mentioned = models.BooleanField(default=False)

    def __str__(self):
        return str(self.feed) + " " + self.title
