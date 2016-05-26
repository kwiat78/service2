from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.views import APIView
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer
import requests

from locations.models import Location
from locations.serializers import LocationSerializer, LocationSerializer2

from rest_framework.response import Response

class LocationView(ModelViewSet):
    queryset = Location.objects.all().order_by("date")
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        return super(LocationView, self).create(request, *args, **kwargs)
        # import ipdb;ipdb.set_trace()


class TrackApiView(APIView):

    def get(self,request,label=None):
        if label:
            return Response(map(lambda x:{'longitude':x.longitude, 'latitude':x.latitude}, Location.objects.filter(label=label).order_by("date")))


        return Response(map(lambda x:x["label"], Location.objects.values("label").distinct()))


    def post(self, request, label):
        new_label = request.data.get("new_label", None)
        if not new_label:
            return Response("Specify new_label", status=403)
        Location.objects.filter(label=label).update(label=new_label)
        return Response(status=200)

    def delete(self,request,label=None):
        if label:
            Location.objects.filter(label=label).delete()
        return Response(status=204)

class JoinTrackApiView(APIView):

    def post(self, request, label):
        second_label = request.data.get("second_label", None)
        if not second_label:
            return Response("Needed second_label", status=403)
        if label == second_label:
            return Response("Labels should be diferent", status=403)
        Location.objects.filter(label=second_label).update(label=label)
        return Response(status=200)




class SnapApiView(APIView):
    def get(self,request,label):
        print("XXXXXXXXXXXXXXXXX")
        url = 'https://roads.googleapis.com/v1/snapToRoads'
        key ="AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"
        interpolate= True
        path = "|".join(list(map(lambda x:str(x.latitude)+","+str(x.longitude), Location.objects.filter(label=label))))
        print(label)
        print(path)

        response = requests.get(url=url,params={"key":key, "interpolate":interpolate,"path":path})
        #res = map(lambda x:x.location, response.json()['snappedPoints'])
        res = map(lambda x:x['location'], response.json()['snappedPoints'])
        #import ipdb;ipdb.set_trace()
        return Response(res)

class StreetApiView(APIView):
    def get(self,request,label):
        key ="AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Location.objects.filter(label=label)
        streets =[]
        for location in locations:
            latlng = str(location.latitude)+","+str(location.longitude)
            response = requests.get(url=url,params={"key":key, "latlng":latlng, "result_type":"route"})
            #import ipdb;ipdb.set_trace()
            routes = list(filter(lambda x: 'route' in x['types'],response.json()['results'][0]['address_components']))
            streets +=[routes[0]['long_name']]
        return Response(streets)


class IntersectionApiView(APIView):
    def get(self,request,label):
        key ="AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        locations = Location.objects.filter(label=label)
        streets =[]
        for location in locations:
            latlng = str(location.latitude)+","+str(location.longitude)
            response = requests.get(url=url,params={"key":key, "latlng":latlng, "result_type":"route"})
            #import ipdb;ipdb.set_trace()
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


class TrackViewSet(ViewSet):

    def list(self, request):
        return Response(map(lambda x:x["label"], Location.objects.values("label").distinct()))

    def retrieve(self, request, pk=None):
        queryset = Location.objects.filter(label=pk)

        serializer = LocationSerializer2(queryset, many=True)
        return Response(serializer.data)

    @detail_route()
    def snap(self,request,pk=None):
        print("XXXXXXXXXXXXXXXXX")
        url = 'https://roads.googleapis.com/v1/snapToRoads'
        key ="AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"
        interpolate= True
        path = "|".join(list(map(lambda x:str(x.latitude)+","+str(x.longitude), Location.objects.filter(label=pk))))



        response = requests.get(url=url,params={"key":key, "interpolate":interpolate,"path":path})
        #res = map(lambda x:x.location, response.json()['snappedPoints'])
        res = map(lambda x:x['location'], response.json()['snappedPoints'])
        #import ipdb;ipdb.set_trace()
        return Response(res)