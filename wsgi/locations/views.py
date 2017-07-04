import json
from math import radians, cos, sin, asin, sqrt

import requests
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Min, Max
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ViewSet

from wsgi.locations.models import Location, Track
from wsgi.locations.serializers import LocationSerializer, TrackSerializer
from wsgi.locations.utils.googleapi import GoogleAPIClient, GeocodingException
from wsgi.locations.utils.map import Map

GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def haversine(lon1, lat1, lon2, lat2):
            """
            Calculate the great circle distance between two points
            on the earth (specified in decimal degrees)
            """
            # convert decimal degrees to radians
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            # haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            km = 6367 * c
            return km


class LocationView(ModelViewSet):
    queryset = Location.objects.none()
    serializer_class = LocationSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Location.objects.filter(track__user=self.request.user).order_by("date")

    def create(self, request, *args, **kwargs):
        username = request.data.get('user')
        track = request.data.get('track')
        if username and track:
            user = User.objects.get(username=username)
            Track.objects.get_or_create(label=track, user=user)
        return super(LocationView, self).create(request, *args, **kwargs)


class TrackViewSet(ModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    lookup_field = 'label'
    lookup_url_kwarg = 'label'

    def get_queryset(self):
        return Track.objects.filter(user=self.request.user)

    def list(self, request):
        return Response(self.get_queryset().values_list("label", flat=True))

    def retrieve(self, request, label=None):
        super().retrieve(request, label=label)
        queryset = Location.objects.filter(track__label=label).order_by("date")
        serializer = TrackSerializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, label=None):
        obj = get_object_or_404(self.get_queryset(), label=label)
        self.check_object_permissions(self.request, obj)
        new_label = request.data.get("new_label", None)

        if not new_label:
            return Response("Specify new_label", status=403)
        obj.label = new_label
        obj.save()
        return Response(status=200)

    @detail_route()
    def params(self, request, label=None):
        obj = get_object_or_404(self.get_queryset(), label=label)
        self.check_object_permissions(self.request, obj)
        points_number = obj.location_set.count()
        start = obj.location_set.aggregate(Min('date'))["date__min"]
        stop = obj.location_set.aggregate(Max('date'))["date__max"]
        processed = obj.procesed
        res = {
            "points_number": points_number,
            "start_date": start,
            "stop_date": stop,
            "processed": processed,
        }
        return Response(res)

    @detail_route()
    def process(self, request, label=None):
        obj = get_object_or_404(self.get_queryset(), label=label)
        self.check_object_permissions(self.request, obj)
        obj.procesed = True
        obj.save()
        return Response(status=201)

    @detail_route()
    def snap(self, request, label=None):
        obj = get_object_or_404(self.get_queryset(), label=label)
        self.check_object_permissions(self.request, obj)
        google_api_client = GoogleAPIClient(settings.GOOGLE_API_KEY)
        res = google_api_client.snap_to_roads(obj.location_set.all())
        return Response(res)

    @detail_route()
    def streets(self, request, label=None):
        obj = get_object_or_404(self.get_queryset(), label=label)
        self.check_object_permissions(self.request, obj)
        locations = obj.location_set.all()
        streets = []
        previous = ""
        google_api_client = GoogleAPIClient(settings.GOOGLE_API_KEY)

        for location in locations:
            try:
                street = google_api_client.geocode(location)
                if street != previous:
                    streets.append(street)
                    previous = street
            except GeocodingException:
                pass
        result = []
        size = len(streets)
        idx = 0
        while idx < size:
            if idx + 2 < size:
                if streets[idx] == streets[idx + 2]:
                    result.append(streets[idx])
                    idx += 3
                else:
                    result.append(streets[idx])
                    idx += 1
            else:
                result.append(streets[idx])
                idx += 1

        return Response(result)

    @detail_route()
    def intersections(self, request, label=None):
        obj = get_object_or_404(self.get_queryset(), label=label)
        self.check_object_permissions(self.request, obj)
        locations = obj.location_set.all()
        streets = []
        google_api_client = GoogleAPIClient(settings.GOOGLE_API_KEY)
        for location in locations:
            try:
                street = google_api_client.geocode(location)
                streets += [street]
            except GeocodingException:
                pass

        points = [{"latitude": locations[0].latitude, "longitude": locations[0].longitude}]

        for i in range(1, len(locations)):
            if streets[i] != streets[i-1]:
                r = requests.get(GEOCODING_URL, params={
                    'address': "{} and {}, Toruń".format(streets[i-1], streets[i]),
                    'key': settings.GOOGLE_API_KEY
                }).json()
                if r['results']:
                    if r['results'][0]['types'][0] == 'intersection':
                        intersection = (r['results'][0]['geometry']['location'])
                        points += [
                            {
                                "latitude": intersection['lat'],
                                "longitude": intersection["lng"]
                            }
                        ]
            points += [
                {
                    "latitude": locations[i].latitude,
                    "longitude":locations[i].longitude
                }
            ]

        return Response(points)

    @detail_route()
    def only_intersections(self, request, label=None):
        obj = get_object_or_404(self.get_queryset(), label=label)
        self.check_object_permissions(self.request, obj)
        locations = obj.location_set.all()
        streets = []
        google_api_client = GoogleAPIClient(settings.GOOGLE_API_KEY)
        for location in locations:
            try:
                street = google_api_client.geocode(location)
                streets += [street]
            except GeocodingException:
                pass

        points = []
        last_point = None
        for i in range(1, len(locations)):
            if streets[i] != streets[i - 1]:
                resp = requests.get(GEOCODING_URL, params={
                    'address': "{} and {}, Toruń".format(streets[i - 1], streets[i]),
                    'key': settings.GOOGLE_API_KEY
                }).json()
                if resp['status'] == 'OK':
                    if resp['results'][0]['types'][0] == 'intersection':
                        intersection = (resp['results'][0]['geometry']['location'])
                        if not last_point:
                            last_point = (intersection['lng'], intersection["lat"])

                        if haversine(last_point[0], last_point[1], intersection['lng'], intersection["lat"]) < 10:
                            last_point = (intersection['lng'], intersection["lat"])
                            points += [
                                {
                                    "latitude": intersection['lat'],
                                    "longitude": intersection["lng"],
                                    "street_a": min(streets[i], streets[i - 1]),
                                    "street_b": max(streets[i], streets[i - 1])
                                }
                            ]
        return Response(points)

    @detail_route(methods=["post"])
    def join(self, request, label=None):
        track = get_object_or_404(self.get_queryset(), label=label)
        self.check_object_permissions(self.request, track)

        second_label = request.data.get("second_label", None)

        if not second_label:
            return Response("Needed second_label", status=403)
        if label == second_label:
            return Response("Labels should be different", status=403)

        second_track = get_object_or_404(self.get_queryset(), label=second_label)
        self.check_object_permissions(self.request, second_track)

        Location.objects.filter(track__label=second_label).update(track=track)
        Track.objects.get(label=second_label).delete()
        return Response(status=200)


class MapViewSet(ViewSet):
    def list(self, request):
        my_map = Map()

        try:
            f = open(settings.MAP_, "r")
            map_json = json.load(f)
            my_map.from_json(map_json)
        except FileNotFoundError:
            pass
        except ValueError:
            pass

        streets = my_map.to_streets()
        res = [
            [
                {
                   'latitude': my_map.get_point(point).latitude,
                   'longitude': my_map.get_point(point).longitude
                } for point in streets[street]
                ] for street in streets]
        return Response(res)
