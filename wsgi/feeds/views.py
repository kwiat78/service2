from binascii import a2b_base64

from bs4 import BeautifulSoup

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import datetime, now

from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet

import urllib
from urllib.parse import unquote


from feeds.celery import get_posts
from feeds.models import Feed, Post, FeedLink, Link
from feeds.serializers import FeedSerializer, PostSerializer, FeedLinkSerializer


class FeedView(ModelViewSet):
    queryset = Feed.objects.all().order_by("position")
    serializer_class = FeedSerializer

    @list_route()
    def loop(self, request, **kwargs):
        return Response(get_posts())

    def retrieve(self, request, pk, **kwargs):
        user = request.META.get("HTTP_USER","")
        feed = Feed.objects.get(user__username=user, name=pk)
        serializer=FeedSerializer(feed)
        return Response(serializer.data)

    def update(self, request, pk, *args, **kwargs):
        user = request.META.get("HTTP_USER","")
        try:
            feed = Feed.objects.get(user__username=user, name=pk)
        except ObjectDoesNotExist:
            return Response({"detail":"Feed does not exist."}, status=404)
        required = ["name","postLimit","favIcon"]
        for param in required:
            if param not in request.data:
                return Response(status=400)
        feed.name = request.data['name']
        feed.postLimit = request.data['postLimit']
        feed.favIcon = request.data['favIcon']
        feed.save()
        return Response(status=200)

    def create(self, request, *args, **kwargs):
        user = request.META.get('HTTP_USER',"")
        name = request.data['name']
        regexp = request.data['regexp']
        url = request.data['url']
        favIcon = request.data.get('favIcon', "undefined")
        position = len(Feed.objects.filter(user__username=user))
        user = User.objects.get(username=user)
        feed = Feed.objects.create(name=name,user=user, position=position, postLimit=10, favIcon=favIcon)
        link,_ = Link.objects.get_or_create(url=url)
        FeedLink.objects.create(feed=feed, link=link, reg_exp=regexp)
        return Response(status=201)

    def destroy(self, request, pk,*args, **kwargs):
        user = request.META.get("HTTP_USER","")
        try:
            feed = Feed.objects.get(user__username=user, name=pk)
        except ObjectDoesNotExist:
            return Response({"detail":"Feed does not exist."}, status=404)
        feed.delete()
        return Response(status=200)

    def list(self, request, *args, **kwargs):
        user = request.META.get("HTTP_USER","")
        feed = Feed.objects.filter(user__username=user)
        return Response(FeedSerializer(feed, many=True).data)


class LinkView(ModelViewSet):
    queryset = FeedLink.objects.all()
    serializer_class = FeedLinkSerializer

    def list(self, request, feed):
        #import ipdb;ipdb.set_trace()
        user = request.META.get("HTTP_USER","")
        return Response(self.serializer_class(self.queryset.filter(feed__name=feed, feed__user__username=user).order_by("position"),
                                              many=True).data)


    def retrieve(self, request, feed, pk,*args, **kwargs):
        user = request.META.get("HTTP_USER","")
        return Response(self.serializer_class(self.queryset.get(feed__name=feed, position=pk, feed__user__username=user)).data)

    def create(self, request, feed,*args, **kwargs):
        #import ipdb;ipdb.set_trace()
        user = request.META.get("HTTP_USER","")
        url = request.data["link"]
        link,_ = Link.objects.get_or_create(url=url)
        feed_obj = Feed.objects.get(name=feed, user__username=user)
        reg_exp = request.data["reg_exp"]
        position = len(self.queryset.filter(feed__name=feed))
        FeedLink.objects.create(feed=feed_obj, link=link, reg_exp=reg_exp, position=position)
        return Response(status=200)

    def update(self, request, feed, pk, *args, **kwargs):
        user = request.META.get("HTTP_USER","")
        url = request.data["link"]
        link,_ = Link.objects.get_or_create(url=url)
        reg_exp = request.data["reg_exp"]

        feedlink=self.queryset.get(feed__name=feed, position=pk, feed__user__username=user)
        #feedlink.feed=feed_obj
        feedlink.link=link
        feedlink.reg_exp = reg_exp
        feedlink.save()

        return Response(status=200)

    def destroy(self, request, feed,pk, *args, **kwargs):
        user = request.META.get("HTTP_USER","")
        feedlink=self.queryset.get(feed__name=feed, position=pk, feed__user__username=user)
        feedlink.delete()
        for fl in FeedLink.objects.filter(position__gt=pk):
            fl.position -=1
            fl.save()
        return Response(status=200)






class PostView(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    http_method_names =("get", "put",)

    # def  create(self, request, *args, **kwargs):
    #     print("create")
    #     print(request)

    def  update(self, request, pk,*args, **kwargs):
        user = request.META.get("HTTP_USER","")
        print("update")
        print(request)
        view = request.data
        #print(pk)
        #print(a2b_base64(pk))
        #import ipdb;ipdb.set_trace()
        url = unquote(a2b_base64(pk).decode())
        print(url)
        print(view)
        x = Post.objects.filter(feed__user__username=user, url=url)
        for xx in x:
            xx.view = view
            xx.save()
        #import ipdb;ipdb.set_trace()
        #print(request)
        return Response(status=200)


    def list(self, request):
        user = request.META.get("HTTP_USER","")
        acceptable = {"name":"feed__name","new":"feed__view"}
        criteria = {}
        count = False

        if "name" in request.GET:
            criteria["feed__name"] = request.GET["name"]

        if "new" in request.GET:
            if request.GET["new"].capitalize()=="True":
                criteria["view"] = False
            if request.GET["new"].capitalize()=="False":
                criteria["view"] = True

        if "curent" in request.GET:
            curent = datetime.fromtimestamp(float(request.GET["curent"]))
            criteria["add_date__gte"]=curent
            criteria["add_date__lte"]=now()


        if "count" in request.GET:
            if request.GET["new"].capitalize()=="True":
                count = True

        print(request.GET)
        print(criteria)


        queryset = Post.objects.filter(feed__user__username=user, **criteria ).order_by("-post_date")
        if count:
            return Response([{"count":queryset.count()}])
        return Response(PostSerializer(queryset, many=True).data)



class ReorderView(APIView):

    def put(self, request):
        user = request.META.get("HTTP_USER","")
        old_pos = int(request.data["oldPosition"])
        new_pos = int(request.data["newPosition"])

        if old_pos>new_pos:
            criteria ={"position__lte":old_pos-1, "position__gte":new_pos}
            change = 1
        if old_pos<new_pos:
            criteria ={"position__gte":old_pos+1, "position__lte":new_pos}
            change = -1
        if old_pos!=new_pos:
            obj = Feed.objects.get(user__username=user, position=old_pos)

            for f in Feed.objects.filter(user__username=user, **criteria):
                f.position = f.position + change
                f.save()
            obj.position = new_pos
            obj.save()

        return Response(status=200)


class TimeView(ViewSet):
    # queryset = None
    # serializer =None
    def list(self, request):
        print(datetime.now().timestamp())
        return Response(datetime.now().timestamp(),status=200)


class DiscoverView(ViewSet):
    def list(self, request):
        if "url" in request.GET:
            url = request.GET["url"]
            url = unquote(a2b_base64(url).decode())
            req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'feed-reader'
            })

            site = urllib.request.urlopen(req).read()

            soup = BeautifulSoup(site, "html")
            links = soup.head.find_all("link",{"type":"application/rss+xml"})
            print([ x.get('href') for x in links])
        return Response([ x.get('href') for x in links],status=200)

class FindView(ViewSet):
    def list(self, request):
        if "url" in request.GET:
            url = request.GET["url"]
            url = unquote(a2b_base64(url).decode())
            req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'feed-reader'
            })

            site = urllib.request.urlopen(req).read()

            soup = BeautifulSoup(site, "xml")
            channel = soup.find("channel")
            if not channel:
                channel = soup.find("feed")
            title = channel.find("title").text
            if title=="":
                title=url


        return Response({"name":title,"url":url},status=200)








