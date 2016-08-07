from django.db.models import Min, Max
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.views import APIView
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer
import requests

from wsgi.locations.models import Location
from wsgi.locations.serializers import LocationSerializer, TrackSerializer

from rest_framework.response import Response

class LocationView(ModelViewSet):
    queryset = Location.objects.all().order_by("date")
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        return super(LocationView, self).create(request, *args, **kwargs)
        # import ipdb;ipdb.set_trace()

class TrackViewSet(ViewSet):

    def list(self, request):
        return Response(map(lambda x:x["label"], Location.objects.values("label").distinct()))

    def retrieve(self, request, pk=None):
        queryset = Location.objects.filter(label=pk)

        serializer = TrackSerializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        new_label = request.data.get("new_label", None)
        if not new_label:
            return Response("Specify new_label", status=403)
        Location.objects.filter(label=pk).update(label=new_label)
        return Response(status=200)

    def destroy(self,request,pk=None):
        if pk:
            Location.objects.filter(label=pk).delete()
        return Response(status=204)

    @detail_route()
    def params(self, request, pk=None):
        points_number = len(Location.objects.filter(label=pk))
        start = Location.objects.filter(label=pk).aggregate(Min('date'))["date__min"]
        stop = Location.objects.filter(label=pk).aggregate(Max('date'))["date__max"]
        res = {
            "points_number": points_number,
            "start_date": start,
            "stop_date": stop,
        }
        return Response(res)

    @detail_route()
    def snap(self,request,pk=None):
        url = 'https://roads.googleapis.com/v1/snapToRoads'
        key ="AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"
        interpolate = True
        path = "|".join(list(map(lambda x:str(x.latitude)+","+str(x.longitude), Location.objects.filter(label=pk))))
        response = requests.get(url=url,params={"key":key, "interpolate":interpolate,"path":path})
        res = map(lambda x:x['location'], response.json()['snappedPoints'])
        return Response(res)

    @detail_route()
    def streets(self,request,pk=None):
        key ="AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Location.objects.filter(label=pk)
        streets =[]
        for location in locations:
            latlng = str(location.latitude)+","+str(location.longitude)
            response = requests.get(url=url,params={"key":key, "latlng":latlng, "result_type":"route"})
            routes = list(filter(lambda x: 'route' in x['types'],response.json()['results'][0]['address_components']))
            streets +=[routes[0]['long_name']]
        return Response(streets)

    @detail_route()
    def intersections(self,request,pk=None):
        key ="AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Location.objects.filter(label=pk)
        streets =[]
        for location in locations:
            latlng = str(location.latitude)+","+str(location.longitude)
            response = requests.get(url=url,params={"key":key, "latlng":latlng, "result_type":"route"})
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

    @detail_route(methods=["post"])
    def join(self, request, pk=None):
        second_label = request.data.get("second_label", None)
        if not second_label:
            return Response("Needed second_label", status=403)
        if pk == second_label:
            return Response("Labels should be diferent", status=403)
        Location.objects.filter(label=second_label).update(label=pk)
        return Response(status=200)
