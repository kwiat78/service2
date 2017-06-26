from __future__ import absolute_import

import urllib
from binascii import a2b_base64
from urllib.parse import unquote

import iso8601
from bs4 import BeautifulSoup
from django.utils.timezone import datetime, now, make_aware, is_naive
from wsgi.feeds.models import Post, FeedLink


def scan_url(url):
    url = unquote(a2b_base64(url).decode())
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'feed-reader'
        })
    site = urllib.request.urlopen(req)

    stream = site.read()
    soup = BeautifulSoup(stream, "html")
    links = soup.head.find_all("link", {"type": "application/rss+xml"})
    return [x.get('href') for x in links]


def extract_feeds(url):
    url = unquote(a2b_base64(url).decode())
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'feed-reader'
        })

    site = urllib.request.urlopen(req)
    stream = site.read()
    soup = BeautifulSoup(stream, "xml")
    channel = soup.find("channel")
    if not channel:
        channel = soup.find("feed")
    if not channel:
        return None
    title = channel.find("title").text
    if title == "":
        title = url
    return {"name": title, "url": url}


class FeedDownloader:
    def __init__(self, url):
        self.url = url
        self.max_posts = get_gratest_limit(url)

    def get_posts(self):
        req = urllib.request.Request(
            self.url,
            data=None,
            headers={
                'User-Agent': 'feed-reader'
            })

        site = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(site, "xml")
        items = soup.findAll("item")
        if len(items) == 0:
            items = soup.findAll("entry")
        posts = []
        for item in items[:self.max_posts]:
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

            post = Post(title=title, url=link,post_date=post_date, add_date=now(), view=False)
            posts+=[post]
        return posts


def get_gratest_limit(url):
    links = FeedLink.objects.filter(link__url=url)
    if len(links) > 0:
        return max([x.feed.postLimit for x in links])
    return 10


