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

from map.orient import sort, sort_2
from map.map import Map, Point

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


class MapViewSet(ViewSet):
    def list(self, request):
        map_in = settings.MAP_
        m = Map()
        # m.from_json(json.load(open(map_in, 'r')))

        try:
            f = open(map_in, "r")
            map_json = json.load(f)
            m.from_json(map_json)
        except FileNotFoundError:
            pass
        except ValueError:
            pass

        X = m.to_streets()
        # XE = {street:[{'latitude': m.get_point(point).latitude, 'longitude': m.get_point(point).longitude} for point in X[street]] for street in X}
        XE = [[{'latitude': m.get_point(point).latitude, 'longitude': m.get_point(point).longitude} for point in X[street]] for street in X]
        return Response(XE)


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
    def with_streets(self, request, pk=None):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Track.objects.get(label=pk).location_set.all()
        points = []
        groups = []
        group = []
        previous = None
        res = []

        for location in locations:
            latlng = str(location.latitude) + "," + str(location.longitude)
            response = requests.get(url=url, params={"key": settings.GOOGLE_API_KEY, "latlng": latlng})
            routes = list(filter(lambda x: 'route' in x['types'], response.json()['results'][0]['address_components']))
            street = routes[0]['long_name']

            if previous and previous != street:
                groups.append(group)
                group = []

            group.append(
                Point({
                    'longitude': location.longitude,
                    'latitude': location.latitude,
                    'street_a': street,
                    'street_b': street
                })
            )

            previous = street
        groups.append(group)

        m = Map()
        try:
            f = open(settings.MAP_, "r")
            map_json = json.load(f)
            m.from_json(map_json)
        except FileNotFoundError:
            pass
        except ValueError:
            pass
        s = m.to_streets()
        for id_g, g in enumerate(groups):
            st = list(g[0].streets)[0]
            if st in s:
                # print(s[st], g)
                x = sort_2(m, s[st][0], s[st][1:], g)

                x2 = [xx[1] for xx in x]
                # print(x2)
                start = x2.index(-1)
                stop = x2.index(-len(g))
                q=False
                if start>stop:
                    q =True
                start,stop = min(start, stop), max(start,stop)
                y = x2[start:stop+1]
                if q:
                    y.reverse()
                print(y)
                z = []
                for yy in y:
                    if yy>=0:
                        poi = m.get_point(yy)

                    else:
                        poi = g[-yy-1]
                    z += [{'latitude': float(poi.latitude), 'longitude': float(poi.longitude)}]
                print(z)

                # print(start,stop)
                # print(x2[start:stop])
                # if id_g+1<len(groups) and stop+1<len(x2) and list(groups[id_g+1][0].streets)[0] in m.get_point(x2[stop+1]).streets:
                #     groups[id_g+1].append(m.get_point(x2[stop+1]))


            else:
                # print('*')
                # x = sort(m, s[st][0], s[st][1:])

                z =[{'latitude': gg.latitude, 'longitude':gg.longitude} for gg in g]
                print(z)
            print(z)
            res.extend(z)
            print(res)
        X = m.to_streets()


        return Response(res)

    @detail_route()
    def intersections(self,request,pk=None):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Track.objects.get(label=pk).location_set.all()
        streets = []
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
        last_point = None
        for i in range(1, len(locations)):
            if streets[i] != streets[i - 1]:
                response = requests.get(url2.format(streets[i - 1], streets[i]))
                resp = response.json()
                print(url2.format(streets[i - 1], streets[i]))
                print(resp)
                if resp['status'] == 'OK':
                    if resp['results'][0]['types'][0] == 'intersection':
                        intersection = (resp['results'][0]['geometry']['location'])
                        if not last_point:
                            last_point = (intersection['lng'], intersection["lat"])

                        if haversine(last_point[0], last_point[1], intersection['lng'], intersection["lat"]) < 10:
                            last_point = (intersection['lng'], intersection["lat"])
                            points += [{"latitude": intersection['lat'], "longitude": intersection["lng"],
                                        "street_a": min(streets[i], streets[i - 1]),
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
