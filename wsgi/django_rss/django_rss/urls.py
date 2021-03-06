from django.conf.urls import include, url
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from wsgi.authentication.urls import urlpatterns as auth_urls
from wsgi.feeds.views import FeedView, PostView, LinkView,  DiscoverView
from wsgi.locations.views import LocationView, TrackViewSet, MapViewSet
from wsgi.webclient.views import index

router = DefaultRouter()
router.register(r"map", MapViewSet, base_name="map")
router.register(r"locations", LocationView)
router.register(r"tracks", TrackViewSet, base_name="tracks")
router.register(r"feeds", FeedView)
router.register(r"posts", PostView)
router.register(r"discover", DiscoverView, base_name="discover")

posts_router = DefaultRouter()
posts_router.register(r"links", LinkView)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/auth/', include(auth_urls)),


    url(r'^api/', include(router.urls)),
    url(r'^api/feeds/(?P<feed>[^/.]+)/', include(posts_router.urls)),
    url(r'^webclient/index', index),
    url(r'^$', index),
]
