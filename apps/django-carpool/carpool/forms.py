from django import forms
from django.utils.translation import ugettext_lazy as _

from carpool.models import Trip
from carpool.fields.geometry import LocationFormField
from carpool.fields.datetime import DateTimeSelectWidget, DateSelectWidget, TimeSelectWidget

from uni_form.helpers import FormHelper, Submit, Reset
from uni_form.helpers import Layout, Fieldset, Row, Column, HTML

TripFormHelper = FormHelper()

layout = Layout(
    Fieldset('',
        Column('email', 'when')),
    
    Fieldset(_('Route'),
        'from_point'
    )
)

TripFormHelper.add_layout(layout)

submit = Submit('add', _('Add this contact'))

TripFormHelper.add_input(submit)

class TripForm(forms.ModelForm):
    
    class Meta:
        model = Trip
        widgets = {'when': DateTimeSelectWidget}
        
    travel_path = LocationFormField(label=_('Route'))

    helper = TripFormHelper


class SearchTripForm(forms.Form):
    
    travel_path = LocationFormField(label=_('Route'))
    day = forms.DateField(label=_('Day'), widget=DateSelectWidget)
    earliest = forms.TimeField(label=_('Earliest'), widget=TimeSelectWidget)
    latest = forms.TimeField(label=_('Latest'), widget=TimeSelectWidget)