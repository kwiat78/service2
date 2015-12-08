from feeds.models import Feed,Link,Post

from bs4 import BeautifulSoup

import urllib
import iso8601


#from datetime import datetime

from feeds.serializers import PostSerializer

from django.utils.timezone import datetime, now, make_aware, is_naive
import re
from copy import deepcopy
from django.conf import  Settings



class FeedDownloader():
    def __init__(self, url):
        self.url = url
        self.max_posts = 20

    def get_posts(self):
        req = urllib.request.Request(
            self.url,
            data=None,
            headers={
                'User-Agent': 'feed-reader'
            })

        site = urllib.request.urlopen(req).read()

        soup = BeautifulSoup(site, "xml")
        #print(soup)
        items = soup.findAll("item")
        if len(items) == 0:
            items = soup.findAll("entry")
        posts = []
        for item in items[:10]:
            title = item.find("title").text

            link = item.find("link")
            if link is not None:
                link_ = link.text
                if link_ == "":
                    link = link.get("href")
                else:
                    link = link_
            else:
                link = item.find("enclosure").get("url")

            post_date = item.find("pubDate")
            if post_date is not None:
                post_date = post_date.text.strip()
            else:
                post_date = item.find("published").text.strip()
            try:
                post_date = datetime.strptime(post_date,"%a, %d %b %Y %H:%M:%S %z")
            except ValueError:
                try:
                    post_date = datetime.strptime(post_date,"%a, %d %b %Y %H:%M:%S %Z")
                except ValueError:
                    post_date = iso8601.parse_date(post_date,)

            if is_naive(post_date):
                post_date = make_aware(post_date)

            #print(title,link,post_date)

            post = Post(title=title, url=link,post_date=post_date, add_date=now(), view=False)
            posts+=[post]
        return posts


from datetime import timedelta

from celery.task import periodic_task



@periodic_task(run_every=timedelta(minutes=5))
def get_posts():
    #print("*")
    #feeds = Feed.objects.all()
    links = Link.objects.all()
    for link in links:
        downloader=FeedDownloader(link.url)
        newest_posts = downloader.get_posts()
        for post in newest_posts:
            for feedLink in link.feedlink_set.all():
                #print(feedLink.feed, feedLink.link)

            #import ipdb; ipdb.set_trace()

                if re.match(feedLink.reg_exp, post.title):
                    posts = Post.objects.filter(url=post.url, feed=feedLink.feed)
                    # print(len(posts))
                    #print(posts)
                    if len(posts)==0:
                        print(post.title,post.url,post.post_date)
                        new_post = deepcopy(post)
                        new_post.feed=feedLink.feed
                        new_post.save()

                    else:
                        if len(posts)==1:
                            p = posts[0]

                            #import ipdb;ipdb.set_trace()
                            from django.utils.timezone import is_aware
                            if p.add_date<post.post_date and p.view==False:
                                #print(p.title,post.title)
                                # print(p.title,post.title)
                                print("#")
                                p.post_date = post.post_date
                                p.add_date = now()
                                p.title = post.title
                                p.url = post.url
                                p.save()
                            # print("*")
                            if p.title!=post.title and post.post_date>p.add_date:
                                # print(p.title,post.title)
                                print("&")
                                #print(p.title, post.title)
                                p.add_date = now()
                                p.post_date = post.post_date
                                p.title = post.title
                                p.save()

    for feed in Feed.objects.all():
        limit = feed.postLimit
        posts = Post.objects.filter(feed=feed).order_by("-post_date")[2*limit:]
        i = len(posts)-1
        while i>0 and posts[i].view:
            posts[i].delete()
            i-=1





    return PostSerializer(newest_posts, many=True).data
