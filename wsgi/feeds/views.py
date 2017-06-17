from urllib.error import URLError

from django.db.models import F
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet
from wsgi.feed_reader.feed_reader import get_posts, scan_url, extract_feeds
from wsgi.feeds.filters import PostFilterBackend
from wsgi.feeds.models import Feed, Post, FeedLink
from wsgi.feeds.pagination import CountPagination
from wsgi.feeds.serializers import FeedSerializer, PostSerializer, FeedLinkSerializer


class FeedView(ModelViewSet):
    queryset = Feed.objects.all().order_by("position")
    serializer_class = FeedSerializer

    def get_queryset(self):
        return Feed.objects.filter(user=self.request.user).order_by("position")

    @list_route(permission_classes=(AllowAny,))
    def loop(self, request, **kwargs):
        return Response(get_posts())

    @list_route(methods=('put',))
    def reorder(self, request):
        user = request.user
        old_pos = int(request.data.get("oldPosition", -1))
        new_pos = int(request.data.get("newPosition", -1))
        if old_pos < 0 or new_pos < 0:
            return Response({"detail": "Wrongly specified positions."}, status=400)

        if old_pos > new_pos:
            criteria = {"position__lte": old_pos - 1, "position__gte": new_pos}
            change = 1
        if old_pos < new_pos:
            criteria = {"position__gte": old_pos + 1, "position__lte": new_pos}
            change = -1
        if old_pos != new_pos:
            obj = Feed.objects.get(user=user, position=old_pos)

            Feed.objects.filter(user=user, **criteria).update(position=F('position') + change)
            obj.position = new_pos
            obj.save()

        return Response(status=200)


class LinkView(ModelViewSet):
    queryset = FeedLink.objects.all()
    serializer_class = FeedLinkSerializer
    lookup_field = "position"

    def get_queryset(self):
        return self.queryset.filter(feed__name=self.kwargs.get('feed'), feed__user=self.request.user)

    def create(self, request, feed, *args, **kwargs):
        user = request.user
        position = len(self.queryset.filter(feed__name=feed))
        feed_obj = Feed.objects.get(name=feed, user=user)
        request.data['feed'] = feed_obj.pk
        request.data['position'] = position
        return super().create(request, feed, *args, **kwargs)

    def destroy(self, request, feed, position, *args, **kwargs):
        result = super().destroy(request, feed, position, *args, **kwargs)
        for fl in FeedLink.objects.filter(position__gt=position):
            fl.position -= 1
            fl.save()
        return result


class PostView(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    http_method_names = ("get", "put", "patch")
    filter_backends = (PostFilterBackend,)
    pagination_class = CountPagination


class DiscoverView(ViewSet):

    @list_route(methods=('get',))
    def scan(self, request):
        x = []
        if "url" in request.GET:
            url = request.GET["url"]
            try:
                x = scan_url(url)
                # site = urllib.request.urlopen(req)
            except URLError:
                return Response({"detail": "Wrong URL."}, status=404)
        return Response(x, status=200)

    @list_route(methods=('get',))
    def extract(self, request):
        x = None
        if "url" in request.GET:
            url = request.GET["url"]
            try:
                x = extract_feeds(url)

            except URLError:
                return Response({"detail": "Wrong URL."}, status=404)
        if x:
            return Response(x, status=200)
        return Response({"detail": "No feeds"}, status=404)
