import json
from math import radians, cos, sin, asin, sqrt

import requests
from django.conf import settings
from django.db.models import Min, Max
from rest_framework.decorators import detail_route
from rest_framework.response import Response
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
    queryset = Location.objects.all().order_by("date")
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        return super(LocationView, self).create(request, *args, **kwargs)


class TrackViewSet(ViewSet):

    def list(self, request):
        return Response(Track.objects.values_list("label", flat=True))

    def retrieve(self, request, pk=None):
        queryset = Location.objects.filter(track__label=pk)

        serializer = TrackSerializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        new_label = request.data.get("new_label", None)

        if not new_label:
            return Response("Specify new_label", status=403)
        track = Track.objects.get(label=pk)
        track.label = new_label
        track.save()
        return Response(status=200)

    def destroy(self,request,pk=None):
        if pk:
            Location.objects.filter(track__label=pk).delete()
            Track.objects.get(label=pk).delete()
        return Response(status=204)

    @detail_route()
    def params(self, request, pk=None):
        points_number = Track.objects.get(label=pk).location_set.count()
        start = Track.objects.get(label=pk).location_set.aggregate(Min('date'))["date__min"]
        stop = Track.objects.get(label=pk).location_set.aggregate(Max('date'))["date__max"]
        processed = Track.objects.get(label=pk).procesed
        res = {
            "points_number": points_number,
            "start_date": start,
            "stop_date": stop,
            "processed": processed,
        }
        return Response(res)

    @detail_route()
    def process(self, request, pk=None):
        track = Track.objects.get(label=pk)
        track.procesed = True
        track.save()
        return Response(status=201)

    @detail_route()
    def snap(self, request, pk=None):
        google_api_client = GoogleAPIClient(settings.GOOGLE_API_KEY)
        res = google_api_client.snap_to_roads(Track.objects.get(label=pk).location_set.all())
        return Response(res)

    @detail_route()
    def streets(self, request, pk=None):
        locations = Track.objects.get(label=pk).location_set.all()
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
    def intersections(self, request, pk=None):
        locations = Track.objects.get(label=pk).location_set.all()
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
    def only_intersections(self, request, pk=None):
        locations = Track.objects.get(label=pk).location_set.all()
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
    def join(self, request, pk=None):
        second_label = request.data.get("second_label", None)
        track = Track.objects.get(label=pk)
        if not second_label:
            return Response("Needed second_label", status=403)
        if pk == second_label:
            return Response("Labels should be different", status=403)
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
