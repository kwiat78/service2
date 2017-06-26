from datetime import datetime
from urllib.error import URLError

import re
from copy import deepcopy

from django.db.models import F, Q
from django.utils.timezone import now, make_aware
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet
from wsgi.feed_reader.feed_reader import scan_url, extract_feeds, FeedDownloader
from wsgi.feeds.filters import PostFilterBackend
from wsgi.feeds.models import Feed, Post, FeedLink, Link
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


def get_posts_old():
    updated = 0
    deleted = 0
    added = 0

    seen = []
    links = Link.objects.all()
    for link in links:
        downloader = FeedDownloader(link.url)
        newest_posts = downloader.get_posts()
        for id, post in enumerate(newest_posts):
            seen += [post.url]
            new_ = True
            for feedLink in link.feedlink_set.all():
                # check if post matches regexp and it's id is lower than the post limit
                if re.match(feedLink.reg_exp, post.title) and id < feedLink.feed.postLimit:
                    posts = Post.objects.filter(url=post.url, feed=feedLink.feed)
                    # post is new
                    if len(posts) == 0 and post.post_date >= get_oldest_post_date(feedLink.feed):
                        print(post.title, post.url, post.post_date)
                        new_post = deepcopy(post)
                        new_post.feed = feedLink.feed
                        new_post.save()
                        if new_:
                            new_ = False
                            added += 1
                    else:
                        if len(posts) == 1:
                            p = posts[0]
                            # unwatched old post was updated
                            if p.add_date < post.post_date and not p.view:
                                p.post_date = post.post_date
                                if post.post_dat > now():
                                    p.add_date = post.post_date
                                else:
                                    p.add_date = now()
                                p.title = post.title
                                p.url = post.url
                                p.save()
                                if new_:
                                    new_ = False
                                    updated += 1
                            # old post updated with a new title
                            if p.title != post.title and post.post_date > p.add_date:
                                p.add_date = now()
                                p.post_date = post.post_date
                                p.title = post.title
                                p.save()
                                if new_:
                                    new_ = False
                                    updated += 1

    for feed in Feed.objects.all():
        limit = feed.postLimit

        posts = Post.objects.filter(feed=feed)
        for post in posts:
            if post.url not in seen:
                post.seen = False
                post.save()
        count = len(posts)

        posts = Post.objects.filter(feed=feed).order_by("post_date")
        for post in posts:
            if not post.seen and post.view and count > limit:
                count -= 1
                post.delete()
                deleted += 1

    return {"added": added, "updated": updated, "deleted": deleted}


def get_posts():
    updated = 0
    deleted = 0
    added = 0

    seen = []
    links = Link.objects.all()
    for link in links:
        downloader = FeedDownloader(link.url)
        newest_posts = downloader.get_posts()
        for id, post in enumerate(newest_posts):
            seen += [post.url]
            new_ = True
            for feedLink in link.feedlink_set.all():
                # check if post matches regexp and it's id is lower than the post limit
                if re.match(feedLink.reg_exp, post.title) and id < feedLink.feed.postLimit:
                    posts = Post.objects.filter(Q(title=post.title) | Q(url=post.url), feed=feedLink.feed)
                    # post is new
                    if len(posts) == 0 and post.post_date >= get_oldest_post_date(feedLink.feed):
                        print(post.title, post.url, post.post_date)
                        new_post = deepcopy(post)
                        new_post.feed = feedLink.feed
                        new_post.save()
                        if new_:
                            new_ = False
                            added += 1
                    else:
                        if len(posts) == 1:
                            p = posts[0]
                            # unwatched old post was updated
                            if p.add_date < post.post_date and not p.view:
                                p.post_date = post.post_date
                                if post.post_dat > now():
                                    p.add_date = post.post_date
                                else:
                                    p.add_date = now()
                                p.title = post.title
                                p.url = post.url
                                p.save()
                                if new_:
                                    new_ = False
                                    updated += 1
                            # old post updated with a new title
                            if p.title != post.title and post.post_date > p.add_date:
                                p.add_date = now()
                                p.post_date = post.post_date
                                p.title = post.title
                                p.save()
                                if new_:
                                    new_ = False
                                    updated += 1

    for feed in Feed.objects.all():
        limit = feed.postLimit

        posts = Post.objects.filter(feed=feed)
        for post in posts:
            if post.url not in seen:
                post.seen = False
                post.save()
        count = len(posts)

        posts = Post.objects.filter(feed=feed).order_by("post_date")
        for post in posts:
            if not post.seen and post.view and count > limit:
                count -= 1
                post.delete()
                deleted += 1

    return {"added": added, "updated": updated, "deleted": deleted}

def get_oldest_post_date(feed):
    pre = Post.objects.filter(feed=feed).order_by("-add_date")[:2*feed.postLimit]
    post = Post.objects.filter(feed=feed).order_by("-add_date")[2*feed.postLimit:]
    if len(pre)==0:
        return make_aware(datetime.fromtimestamp(0))
    if len(post)==0:
        return pre.last().add_date
    else:
        oldest = pre.last().add_date
        for p in post:
            if p.view:
                oldest = p.add_date
        return oldest
