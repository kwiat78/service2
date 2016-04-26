from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer
import requests

from locations.models import Location
from locations.serializers import LocationSerializer

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
            return Response(map(lambda x:{'longitude':x.longitude, 'latitude':x.latitude}, Location.objects.filter(label=label)))


        return Response(map(lambda x:x["label"], Location.objects.values("label").distinct()))


    def post(self, request, label):
        new_label = request.data.get("new_label", None)
        if not new_label:
            return Response("Specify new_label", status=403)
        Location.objects.filter(label=label).update(label=new_label)
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





