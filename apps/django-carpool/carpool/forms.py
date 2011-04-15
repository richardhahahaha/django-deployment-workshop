from django import forms
from carpool.models import Trip
from carpool.fields import LocationFormField, LocationWidget

class TripForm(forms.ModelForm):
    
    class Meta:
        model = Trip
        
    from_point = LocationFormField(widget=LocationWidget, label="Fra")
    to_point = LocationFormField(widget=LocationWidget, label="Til")
