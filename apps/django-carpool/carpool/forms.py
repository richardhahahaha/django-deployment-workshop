from django import forms
from carpool.models import Trip
from carpool.fields.geometry import LocationFormField
from carpool.fields.datetime import DateTimeSelectWidget, DateSelectWidget, TimeSelectWidget

class TripForm(forms.ModelForm):
    
    class Meta:
        model = Trip
        widgets = {'when': DateTimeSelectWidget}
        
    from_point = LocationFormField(label="Fra")
    to_point = LocationFormField(label="Til")

class SearchTripForm(forms.Form):
    
    from_point = LocationFormField(label="Fra")
    to_point = LocationFormField(label="Til")
    day = forms.DateField(label="Dag", widget=DateSelectWidget)
    earliest = forms.TimeField(label="Tidligst", widget=TimeSelectWidget)
    latest = forms.TimeField(label="Senest", widget=TimeSelectWidget)