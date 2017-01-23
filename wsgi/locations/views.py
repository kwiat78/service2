from math import radians, cos, sin, asin, sqrt

import json
import requests

from django.conf import settings
from django.db.models import Min, Max

from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from wsgi.locations.models import Location, Track
from wsgi.locations.serializers import LocationSerializer, TrackSerializer


class LocationView(ModelViewSet):
    queryset = Location.objects.all().order_by("date")
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        return super(LocationView, self).create(request, *args, **kwargs)


# class Map2ViewSet(ViewSet):
#
#     def list(self, request):
#         try:
#             f = open(settings.MAP2, "r")
#             map = json.loads(f.read())
#         except FileNotFoundError:
#             map = []
#         except ValueError:
#             map = []
#
#         return Response(map)
#

class MapViewSet(ViewSet):

    def list(self, request):
        try:
            f = open(settings.MAP, "r")
            map = json.loads(f.read())
        except FileNotFoundError:
            map = []
        except ValueError:
            map = []

        return Response(map)

    @list_route()
    def train(self, request):

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

        tracks = requests.get("http://service2-kwiat78.rhcloud.com/api/tracks").json()

        track = []
        limit = 20
        current = 0
        for t in tracks:
            params = requests.get("http://service2-kwiat78.rhcloud.com/api/tracks/" + t + "/params")
            processed = params.json()["processed"]
            if not processed:
                xx = requests.get("http://service2-kwiat78.rhcloud.com/api/tracks/" + t + "/only_intersections")
                if xx.status_code == 200:
                    ox = xx.json()
                    for o in ox:
                        track.append(o)
                    requests.get("http://service2-kwiat78.rhcloud.com/api/tracks/" + t + "/process")
                    current += 1
            if current == limit:
                break
        try:
            f = open(settings.MAP, "r")
            streets = json.load(f)
        except FileNotFoundError:
            streets = {}
        except ValueError:
            streets = {}

        for point in track:
            street_a = point["street_a"]
            street_b = point["street_b"]
            lng = point["longitude"]
            ltd = point["latitude"]

            for x, y in ((street_a, street_b), (street_b, street_a)):
                if x not in streets:
                    streets[x] = []
                if not streets[x]:
                    streets[x].append([y, lng, ltd])
                elif len(streets[x]) == 1:
                    if streets[x][0][1] < lng:
                        streets[x].append([y, lng, ltd])
                    elif streets[x][0][1] != lng or streets[x][0][2] != ltd:
                        streets[x].insert(0, [y, lng, ltd])
                else:
                    if [y, lng, ltd] not in streets[x]:
                        streets[x].insert(0, [y, lng, ltd])
                        i = 0
                        placed = False
                        while i + 2 < len(streets[x]) and not placed:
                            lng1 = streets[x][i][1]
                            ltd1 = streets[x][i][2]

                            lng2 = streets[x][i + 1][1]
                            ltd2 = streets[x][i + 1][2]

                            lng3 = streets[x][i + 2][1]
                            ltd3 = streets[x][i + 2][2]

                            a = haversine(lng1, ltd1, lng2, ltd2)
                            b = haversine(lng2, ltd2, lng3, ltd3)
                            c = haversine(lng1, ltd1, lng3, ltd3)

                            if a < c and b < c:
                                placed = True
                            elif c < b and a < b:
                                placed = True
                                streets[x][i], streets[x][i + 1] = streets[x][i + 1], streets[x][i]
                            else:
                                streets[x][i], streets[x][i + 1] = streets[x][i + 1], streets[x][i]
                            i += 1
                        if not placed:
                            streets[x][i], streets[x][i + 1] = streets[x][i + 1], streets[x][i]

        with open(settings.MAP, "w") as f:
            json.dump(streets, f)
        return Response(status=201)


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
    def snap(self,request,pk=None):
        url = 'https://roads.googleapis.com/v1/snapToRoads'

        interpolate = True
        path = "|".join(list(map(lambda x:str(x.latitude)+","+str(x.longitude), Track.objects.get(label=pk).location_set.all())))
        response = requests.get(url=url,params={"key": settings.GOOGLE_API_KEY, "interpolate":interpolate,"path":path})
        res = map(lambda x:x['location'], response.json()['snappedPoints'])
        return Response(res)

    @detail_route()
    def streets(self, request, pk=None):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Track.objects.get(label=pk).location_set.all()
        streets = []
        previous = ""
        for location in locations:
            latlng = str(location.latitude) + "," + str(location.longitude)
            response = requests.get(url=url, params={"key": settings.GOOGLE_API_KEY, "latlng": latlng})
            routes = list(filter(lambda x: 'route' in x['types'], response.json()['results'][0]['address_components']))
            street = routes[0]['long_name']
            if street != previous:
                streets.append(street)
                previous = street
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
    def intersections(self,request,pk=None):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Track.objects.get(label=pk).location_set.all()
        streets =[]
        for location in locations:
            latlng = str(location.latitude)+","+str(location.longitude)
            response = requests.get(url=url,params={"key": settings.GOOGLE_API_KEY, "latlng":latlng})
            routes = list(filter(lambda x: 'route' in x['types'],response.json()['results'][0]['address_components']))
            streets +=[routes[0]['long_name']]

        points = [{"latitude":locations[0].latitude, "longitude":locations[0].longitude}]
        url2="https://maps.googleapis.com/maps/api/geocode/json?address={} and {}, Toruń &key=AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"

        for i in range(1,len(locations)):
            if(streets[i]!=streets[i-1]):
                r = requests.get(url2.format(streets[i-1],streets[i])).json()
                if r['results'][0]['types'][0]=='intersection':
                    intersection = (r['results'][0]['geometry']['location'])
                    points+=[{"latitude":intersection['lat'], "longitude":intersection["lng"]}]
            points+=[{"latitude":locations[i].latitude, "longitude":locations[i].longitude}]

        return Response(points)

    @detail_route()
    def only_intersections(self, request, pk=None):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Track.objects.get(label=pk).location_set.all()
        streets = []
        for location in locations:
            latlng = str(location.latitude) + "," + str(location.longitude)
            response = requests.get(url=url, params={"key": settings.GOOGLE_API_KEY, "latlng": latlng})
            routes = list(filter(lambda x: 'route' in x['types'], response.json()['results'][0]['address_components']))
            streets += [routes[0]['long_name']]

        # points = [{"latitude": locations[0].latitude, "longitude": locations[0].longitude}]
        points = []
        url2 = "https://maps.googleapis.com/maps/api/geocode/json?address={} and {}, Toruń &key=AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"

        for i in range(1, len(locations)):
            if (streets[i] != streets[i - 1]):
                response = requests.get(url2.format(streets[i - 1], streets[i]))
                resp = response.json()
                print(url2.format(streets[i - 1], streets[i]))
                print(resp)
                if resp['status']=='OK':
                    if resp['results'][0]['types'][0] == 'intersection':
                        # print(response.status_code)
                        intersection = (resp['results'][0]['geometry']['location'])
                        points += [{"latitude": intersection['lat'], "longitude": intersection["lng"],
                                    "street_a": min(streets[i],streets[i - 1]),
                                    "street_b": max(streets[i], streets[i - 1])}]
            # points += [{"latitude": locations[i].latitude, "longitude": locations[i].longitude}]

        return Response(points)

    @detail_route(methods=["post"])
    def join(self, request, pk=None):
        second_label = request.data.get("second_label", None)
        track = Track.objects.get(label=pk)
        if not second_label:
            return Response("Needed second_label", status=403)
        if pk == second_label:
            return Response("Labels should be diferent", status=403)
        Location.objects.filter(track__label=second_label).update(track=track)
        Track.objects.get(label=second_label).delete()
        return Response(status=200)
