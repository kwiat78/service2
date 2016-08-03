from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, SlugRelatedField

from wsgi.locations.models import Location


class LocationSerializer(ModelSerializer):

    user = SlugRelatedField(slug_field="username",queryset=User.objects.all())

    class Meta:
        model = Location


class TrackSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ('latitude', 'longitude')
