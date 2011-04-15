from django.views import generic
from carpool.models import Trip
from carpool.forms import TripForm

class TripCreate(generic.CreateView):
    model = Trip
    form_class = TripForm
    success_url = '/list/authors/'
    
class TripEdit(generic.UpdateView):
    model = Trip
    form_class = TripForm
    success_url = '/list/authors/'