from django.contrib.gis import admin
from carpool.models import Trip

admin.site.register(Trip, admin.OSMGeoAdmin)