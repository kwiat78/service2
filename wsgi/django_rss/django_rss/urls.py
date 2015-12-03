"""django_rss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from feeds.views import FeedView, PostView, ReorderView, FeedLink, LinkView, TimeView, DiscoverView, FindView

router = DefaultRouter()
router.register(r"feeds", FeedView)
router.register(r"posts", PostView)
router.register(r"time", TimeView, base_name="times")
router.register(r"discover", DiscoverView, base_name="discover")
router.register(r"find", FindView, base_name="discover")

posts_router = DefaultRouter()
posts_router.register(r"links", LinkView)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/reorder', ReorderView.as_view()),


    url(r'^api/', include(router.urls)),
    url(r'^api/feeds/(?P<feed>[^/.]+)/', include(posts_router.urls)),
]
