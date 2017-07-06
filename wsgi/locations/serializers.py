from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, SlugRelatedField

from wsgi.locations.models import Location, Track


class LocationSerializer(ModelSerializer):

    track = SlugRelatedField(slug_field="label", queryset=Track.objects.all())

    class Meta:
        model = Location


class TrackSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ('latitude', 'longitude', 'date')


class SimpleTrackSerializer(ModelSerializer):
    user = SlugRelatedField(slug_field="username", queryset=User.objects.all())

    class Meta:
        model = Track
        fields = ('label', 'user', 'ended')
