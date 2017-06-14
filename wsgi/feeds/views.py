from binascii import a2b_base64

from bs4 import BeautifulSoup

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.utils.timezone import datetime


from rest_framework.decorators import list_route

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet

import urllib
from urllib.parse import unquote
from urllib.error import URLError

from wsgi.feeds.celery import get_posts, scan_url, extract_feeds
from wsgi.feeds.filters import PostFilterBackend
from wsgi.feeds.models import Feed, Post, FeedLink, Link
from wsgi.feeds.pagination import CountPagination
from wsgi.feeds.serializers import FeedSerializer, PostSerializer, FeedLinkSerializer


class FeedView(ModelViewSet):
    queryset = Feed.objects.all().order_by("position")
    serializer_class = FeedSerializer
    # lookup_field = 'name'

    def get_queryset(self):
        return Feed.objects.filter(user=self.request.user).order_by("position")

    @list_route(permission_classes=(AllowAny,))
    def loop(self, request, **kwargs):
        return Response(get_posts())

    # def perform_create(self, serializer):
    #     # import ipdb;ipdb.set_trace()
    #     position = len(Feed.objects.filter(user=serializer.user))
    #     serializer.position = position + 1
    #     super.serializer()

    # def update(self, request, pk, *args, **kwargs):
    #     user = request.user
    #     try:
    #         feed = Feed.objects.get(user=user, id=pk)
    #     except ObjectDoesNotExist:
    #         return Response({"detail": "Feed does not exist."}, status=404)
    #     required = ["name", "postLimit", "favIcon"]
    #     for param in required:
    #         if param not in request.data:
    #             return Response(status=400)
    #     feed.name = request.data['name']
    #     feed.postLimit = request.data['postLimit']
    #     feed.favIcon = request.data['favIcon']
    #     feed.save()
    #     return Response(status=200)

    # def create(self, request, *args, **kwargs):
    #     user = request.user
    #     name = request.data.get('name', "")
    #     if name == "":
    #         return Response(status=400)
    #     regexp = request.data.get('regExp', "")
    #     url = request.data.get('url', "")
    #     favIcon = request.data.get('favIcon', "undefined")
    #     position = len(Feed.objects.filter(user=user))
    #     feed = Feed.objects.create(name=name, user=user, position=position, postLimit=10, favIcon=favIcon)
    #     link, _ = Link.objects.get_or_create(url=url)
    #     FeedLink.objects.create(feed=feed, link=link, reg_exp=regexp)
    #     return Response(status=201)

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
                # f.position += change
                # f.save()
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
    # def create(self, request, feed, *args, **kwargs):
    #     user = request.user
    #     url = request.data.get("link", "")
    #     link, _ = Link.objects.get_or_create(url=url)
    #     try:
    #         feed_obj = Feed.objects.get(name=feed, user=user)
    #     except ObjectDoesNotExist:
    #         return Response({"detail": "Feed does not exist."}, status=404)
    #     reg_exp = request.data.get("reg_exp", "")
    #     position = len(self.queryset.filter(feed__name=feed))
    #     FeedLink.objects.create(feed=feed_obj, link=link, reg_exp=reg_exp, position=position)
    #     return Response(status=201)



    # def update(self, request, feed, position, *args, **kwargs):
    #     user = request.user
    #     url = request.data.get("link", "")
    #     link, _ = Link.objects.get_or_create(url=url)
    #     reg_exp = request.data.get("reg_exp", "")
    #     try:
    #         feedlink = self.queryset.get(feed__name=feed, position=position, feed__user=user)
    #     except ObjectDoesNotExist:
    #         return Response({"detail": "Feed's Link does not exist."}, status=404)
    #
    #     feedlink.link = link
    #     feedlink.reg_exp = reg_exp
    #     feedlink.save()
    #
    #     return Response(status=200)

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

    # def update(self, request, pk, *args, **kwargs):
    #     user = request.user
    #     view = request.data.get('view', None)
    #     mention = request.data.get('mention', None)
    #     url = unquote(a2b_base64(pk).decode())
    #
    #     x = Post.objects.filter(feed__user=user, url=url)
    #     for xx in x:
    #         if view is not None:
    #             xx.view = view
    #         if mention is not None:
    #             xx.mentioned = mention
    #         xx.save()
    #     return Response(status=200)


# class ReorderView(APIView):
#
#     def put(self, request):
#
#         user = request.user
#         old_pos = int(request.data.get("oldPosition", -1))
#         new_pos = int(request.data.get("newPosition", -1))
#         if old_pos < 0 or new_pos < 0:
#             return Response({"detail": "Wrongly specified positions."}, status=400)
#
#         if old_pos > new_pos:
#             criteria = {"position__lte": old_pos - 1, "position__gte": new_pos}
#             change = 1
#         if old_pos < new_pos:
#             criteria = {"position__gte": old_pos + 1, "position__lte": new_pos}
#             change = -1
#         if old_pos != new_pos:
#             obj = Feed.objects.get(user=user, position=old_pos)
#
#             for f in Feed.objects.filter(user=user, **criteria):
#                 f.position += change
#                 f.save()
#             obj.position = new_pos
#             obj.save()
#
#         return Response(status=200)


# class TimeView(ViewSet):
#     def list(self, request):
#         return Response(datetime.now().timestamp(), status=200)


class DiscoverView(ViewSet):

    @list_route(methods=('get',))
    def scan(self, request):
        x = []
        if "url" in request.GET:
            url = request.GET["url"]
            # url = unquote(a2b_base64(url).decode())
            # req = urllib.request.Request(
            #     url,
            #     data=None,
            #     headers={
            #         'User-Agent': 'feed-reader'
            #     })
            try:
                x = scan_url(url)
                # site = urllib.request.urlopen(req)
            except URLError:
                return Response({"detail": "Wrong URL."}, status=404)
            # stream = site.read()
            # soup = BeautifulSoup(stream, "html")
            # links = soup.head.find_all("link", {"type": "application/rss+xml"})
            # print([x.get('href') for x in links])
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
            # url = unquote(a2b_base64(url).decode())
            # req = urllib.request.Request(
            #     url,
            #     data=None,
            #     headers={
            #         'User-Agent': 'feed-reader'
            #     })
            # try:
            #     site = urllib.request.urlopen(req)
            # except URLError:
            #     return Response({"detail": "Wrong URL."}, status=404)
            # stream = site.read()
            # soup = BeautifulSoup(stream, "xml")
            # channel = soup.find("channel")
            # if not channel:
            #     channel = soup.find("feed")
            # if not channel:
            #     return Response({"detail": "Wrong URL."}, status=404)
            # title = channel.find("title").text
            # if title == "":
            #     title = url


