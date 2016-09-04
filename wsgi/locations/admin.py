from django.contrib import admin

from wsgi.locations.models import Location, Track

admin.site.register(Location)
admin.site.register(Track)