from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from carpool.views import TripCreate, TripEdit, TripSearch, TripList, TripAdded, CarPoolFront
    
urlpatterns = patterns('',
    url(r'^$', CarPoolFront.as_view(), name="carpool_front"),
    url(r'^create/$', TripCreate.as_view(), name="carpool_create"),
    url(r'^added/$', TripAdded.as_view(), name="carpool_added"),
    url(r'^list/$', TripList.as_view(), name="carpool_list"),
    url(r'^edit/(?P<pk>\d+)/$', TripEdit.as_view(), name="carpool_edit"),
    url(r'^search/$', TripSearch.as_view(), name="carpool_search"),
    url(r'^admin/', include(admin.site.urls)),
)
