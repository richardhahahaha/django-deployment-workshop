from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from carpool.views import TripCreate

urlpatterns = patterns('',
    url(r'^create/$', TripCreate.as_view()),
    url(r'^admin/', include(admin.site.urls)),
)
