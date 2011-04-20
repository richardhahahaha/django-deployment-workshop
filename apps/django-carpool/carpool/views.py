from django.views import generic
from carpool.models import Trip
from carpool.forms import TripForm, SearchTripForm
from django.contrib.gis.measure import D
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Q
from django.contrib.gis.maps.google import GoogleMap, GMarker, GImage
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.conf import settings

class TripCreate(generic.CreateView):
    model = Trip
    form_class = TripForm
    
    def get_success_url(self):
        return reverse("carpool_added")
    
class TripEdit(generic.UpdateView):
    model = Trip
    form_class = TripForm
    
    def get_success_url(self):
        return reverse("carpool_added")
    
class TripSearch(generic.FormView):
    form_class = SearchTripForm
    template_name = 'carpool/trip_search_form.html'

    def form_valid(self, form):
        search_data = form.cleaned_data
        trips = Trip.objects.filter(
            Q(from_point__distance_lt=(search_data['from_point'], D(km=2))) &
            Q(to_point__distance_lt=(search_data['to_point'], D(km=2)))
        )
        markers = []
        n = 0
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for trip in trips:
            letter = letters[n]
            n = n+1
            kw = dict(size=(20, 34), origin=(0, 0), anchor=(10, 34))
            green = GImage('%smap_icons/green_Marker%s.png' % (settings.STATIC_URL, letter), **kw)
            red = GImage('%smap_icons/red_Marker%s.png' % (settings.STATIC_URL, letter), **kw)
            markers.append(GMarker(trip.from_point, "From", icon=green))
            markers.append(GMarker(trip.to_point, "To", icon=red))
        return direct_to_template(self.request, 'carpool/trip_search_results.html', {
                'map': GoogleMap(
                    markers=markers
                )
            }
        )

class TripAdded(generic.TemplateView):
    template_name = 'carpool/trip_added.html'
    
class TripList(generic.TemplateView):
    template_name = 'carpool/trip_list.html'
    
    def get_context_data(self, **kwargs):
        trips = Trip.objects.all()
        markers = []
        n = 0
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for trip in trips:
            letter = letters[n]
            n = n+1
            kw = dict(size=(20, 34), origin=(0, 0), anchor=(10, 34))
            green = GImage('%smap_icons/green_Marker%s.png' % (settings.STATIC_URL, letter), **kw)
            red = GImage('%smap_icons/red_Marker%s.png' % (settings.STATIC_URL, letter), **kw)
            markers.append(GMarker(trip.from_point, "From", icon=green))
            markers.append(GMarker(trip.to_point, "To", icon=red))
        return {
            'map': GoogleMap(
                markers=markers
            )
        }

        
class CarPoolFront(generic.TemplateView):
    template_name = 'carpool/front.html'
