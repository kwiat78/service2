from django.conf.urls import include, url
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from feeds.views import FeedView, PostView, ReorderView, FeedLink, LinkView, TimeView, DiscoverView, FindView
from locations.views import LocationView, TrackApiView, SnapApiView, StreetApiView, IntersectionApiView
# from webclient.views import index

router = DefaultRouter()
router.register(r"locations", LocationView)
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

    url(r'^api/tracks/(?P<label>[^/.]+)/intersections', IntersectionApiView.as_view()),
    url(r'^api/tracks/(?P<label>[^/.]+)/snap_to_road', SnapApiView.as_view()),
    url(r'^api/tracks/(?P<label>[^/.]+)/streets', StreetApiView.as_view()),
    url(r'^api/tracks/(?P<label>[^/.]+)', TrackApiView.as_view()),

    url(r'^api/tracks', TrackApiView.as_view()),
    # url(r'^webclient/index', index),

]
