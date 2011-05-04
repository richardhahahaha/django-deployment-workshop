from django import forms
from django.utils.translation import ugettext_lazy as _

from carpool.models import Trip
from carpool.fields.geometry import DirectionsFormField
from carpool.fields.datetime import DateTimeSelectWidget, DateSelectWidget, TimeSelectWidget

from uni_form.helpers import FormHelper, Submit, Reset
from uni_form.helpers import Layout, Fieldset, Row, Column, HTML

TripFormHelper = FormHelper()

layout = Layout(
    Fieldset(_('Trip details'),
        Column('email', 'when'), css_class='span-5'),
    
    Fieldset(_('Route'),
        'travel_path', css_class='span-15')
)

TripFormHelper.add_layout(layout)

submit = Submit('add', _('Add this contact'))

TripFormHelper.add_input(submit)

class TripForm(forms.ModelForm):
    
    class Meta:
        model = Trip
        widgets = {'when': DateTimeSelectWidget}
        
    travel_path = DirectionsFormField(label=_('Route'))

    helper = TripFormHelper

SearchTripFormHelper = FormHelper()

layout = Layout(
    Fieldset(_('Trip details'),
        Column('day', 'earliest', 'latest'), css_class='span-5'),
    
    Fieldset(_('Route'),
        'travel_path', css_class='span-15')
)

SearchTripFormHelper.add_layout(layout)

submit = Submit('add', _('Add this contact'))

SearchTripFormHelper.add_input(submit)

class SearchTripForm(forms.Form):
    
    travel_path = DirectionsFormField(label=_('Route'))
    day = forms.DateField(label=_('Day'), widget=DateSelectWidget)
    earliest = forms.TimeField(label=_('Earliest'), widget=TimeSelectWidget)
    latest = forms.TimeField(label=_('Latest'), widget=TimeSelectWidget)
    
    helper = SearchTripFormHelper