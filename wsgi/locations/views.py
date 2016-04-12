from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

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
        return Response(map(lambda x:x.label, Location.objects.all()))
