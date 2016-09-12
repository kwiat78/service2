from django.db.models import Min, Max
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.views import APIView
from rest_framework.decorators import detail_route, list_route
from rest_framework.renderers import JSONRenderer


from django.conf import settings
import json
from math import radians, cos, sin, asin, sqrt
import requests

from wsgi.locations.models import Location, Track
from wsgi.locations.serializers import LocationSerializer, TrackSerializer

from rest_framework.response import Response

class LocationView(ModelViewSet):
    queryset = Location.objects.all().order_by("date")
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        return super(LocationView, self).create(request, *args, **kwargs)
        # import ipdb;ipdb.set_trace()

class MapViewSet(ViewSet):

    def list(self, request):
        map = []
        with open(settings.MAP, "r") as f:
            map = json.loads(f.read())
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
        limit = 2
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
                    print(200)
                    requests.get("http://service2-kwiat78.rhcloud.com/api/tracks/" + t + "/process")
                    current += 1
                    # TODO set_processed
                else:
                    print(500)
            if current == limit:
                break

        # with open("track_a.json", "r") as f:
        streets = {}
        # track = json.loads(f.read().replace("'", "\""))

        try:
            f = open(settings.MAP, "r")
            streets = json.load(f)
        except FileNotFoundError:
            streets = {}
        except ValueError:
            streets = {}
        print(streets)

        for point in track:
            street_a = point["street_a"]
            street_b = point["street_b"]
            lng = point["longitude"]
            ltd = point["latitude"]
            if street_a not in streets:
                streets[street_a] = []
            if not streets[street_a]:
                streets[street_a].append([street_b, lng, ltd])
            elif len(streets[street_a]) == 1:
                if streets[street_a][0][1] < lng:
                    # print(street_a, streets[street_a][0][1] , street_b, lng)
                    streets[street_a].append([street_b, lng, ltd])
                elif streets[street_a][0][1] == lng and streets[street_a][0][2] == ltd:
                    pass
                else:
                    streets[street_a].insert(0, [street_b, lng, ltd])

                    # print(street_a, streets[street_a][0][1], street_b, lng)
            else:
                if [street_b, lng, ltd] not in streets[street_a]:
                    streets[street_a].insert(0, [street_b, lng, ltd])
                    i = 0
                    placed = False
                    while i + 2 < len(streets[street_a]) and not placed:
                        lng1 = streets[street_a][i][1]
                        ltd1 = streets[street_a][i][2]

                        lng2 = streets[street_a][i + 1][1]
                        ltd2 = streets[street_a][i + 1][2]

                        # if lng1 == lng2 and ltd1 == ltd2:
                        #     placed == True
                        #     del streets[street_a][i]
                        #     break

                        lng3 = streets[street_a][i + 2][1]
                        ltd3 = streets[street_a][i + 2][2]

                        a = haversine(lng1, ltd1, lng2, ltd2)
                        b = haversine(lng2, ltd2, lng3, ltd3)
                        c = haversine(lng1, ltd1, lng3, ltd3)

                        if a < c and b < c:
                            placed = True
                        elif c < b and a < b:
                            placed = True
                            streets[street_a][i], streets[street_a][i + 1] = streets[street_a][i + 1], \
                                                                             streets[street_a][i]
                        else:
                            streets[street_a][i], streets[street_a][i + 1] = streets[street_a][i + 1], \
                                                                             streets[street_a][i]
                        i += 1
                    if not placed:
                        streets[street_a][i], streets[street_a][i + 1] = streets[street_a][i + 1], streets[street_a][i]

            if street_b not in streets:
                streets[street_b] = []
            if not streets[street_b]:
                streets[street_b].append([street_a, lng, ltd])
            elif len(streets[street_b]) == 1:
                if streets[street_b][0][1] < lng:
                    streets[street_b].append([street_a, lng, ltd])

                elif streets[street_b][0][1] == lng and streets[street_b][0][2] == ltd:
                    pass
                else:
                    streets[street_b].insert(0, [street_a, lng, ltd])
            else:

                if [street_a, lng, ltd] not in streets[street_b]:

                    streets[street_b].insert(0, [street_a, lng, ltd])
                    i = 0
                    placed = False
                    while i + 2 < len(streets[street_b]) and not placed:

                        lng1 = streets[street_b][i][1]
                        ltd1 = streets[street_b][i][2]

                        lng2 = streets[street_b][i + 1][1]
                        ltd2 = streets[street_b][i + 1][2]

                        lng3 = streets[street_b][i + 2][1]
                        ltd3 = streets[street_b][i + 2][2]

                        a = haversine(lng1, ltd1, lng2, ltd2)
                        b = haversine(lng2, ltd2, lng3, ltd3)
                        c = haversine(lng1, ltd1, lng3, ltd3)

                        if a < c and b < c:
                            placed = True
                        elif c < b and a < b:
                            placed = True
                            streets[street_b][i], streets[street_b][i + 1] = streets[street_b][i + 1], \
                                                                             streets[street_b][i]
                        else:
                            streets[street_b][i], streets[street_b][i + 1] = streets[street_b][i + 1], \
                                                                             streets[street_b][i]
                        i += 1
                    if not placed:
                        streets[street_b][i], streets[street_b][i + 1] = streets[street_b][i + 1], streets[street_b][i]
        print("\n")
        print("\n")
        print(streets)
        with open(settings.MAP, "w") as f:
            json.dump(streets, f)


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
        key ="AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"
        interpolate = True
        path = "|".join(list(map(lambda x:str(x.latitude)+","+str(x.longitude), Track.objects.get(label=pk).location_set.all())))
        response = requests.get(url=url,params={"key":key, "interpolate":interpolate,"path":path})
        res = map(lambda x:x['location'], response.json()['snappedPoints'])
        return Response(res)

    @detail_route()
    def streets(self, request, pk=None):
        key = "AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Track.objects.get(label=pk).location_set.all()
        streets = []
        previous = ""
        for location in locations:
            latlng = str(location.latitude) + "," + str(location.longitude)
            response = requests.get(url=url, params={"key": key, "latlng": latlng})
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
        key ="AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Track.objects.get(label=pk).location_set.all()
        streets =[]
        for location in locations:
            latlng = str(location.latitude)+","+str(location.longitude)
            response = requests.get(url=url,params={"key":key, "latlng":latlng})
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
        key = "AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Track.objects.get(label=pk).location_set.all()
        streets = []
        for location in locations:
            latlng = str(location.latitude) + "," + str(location.longitude)
            response = requests.get(url=url, params={"key": key, "latlng": latlng})
            routes = list(filter(lambda x: 'route' in x['types'], response.json()['results'][0]['address_components']))
            streets += [routes[0]['long_name']]

        # points = [{"latitude": locations[0].latitude, "longitude": locations[0].longitude}]
        points = []
        url2 = "https://maps.googleapis.com/maps/api/geocode/json?address={} and {}, Toruń &key=AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"

        for i in range(1, len(locations)):
            if (streets[i] != streets[i - 1]):
                r = requests.get(url2.format(streets[i - 1], streets[i])).json()
                if r['results'][0]['types'][0] == 'intersection':
                    intersection = (r['results'][0]['geometry']['location'])
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
