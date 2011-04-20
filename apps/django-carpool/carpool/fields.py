from django import forms
from django.db import models
from django.utils.safestring import mark_safe
from django.contrib.gis.geos import *
from django.contrib.gis.db import models
from django.contrib.gis.forms.fields import GeometryField
from django.conf import settings

DEFAULT_WIDTH = 400
DEFAULT_HEIGHT = 300

DEFAULT_EWKT = u'SRID=4326;POINT(10.7522 59.9136)'

import re
POINT_RE = re.compile("SRID=\d+;POINT\s?\((?P<lng>\-?\d+\.\d+)\s(?P<lat>\-?\d+\.\d+)\)")

def point_to_latlng(value):
    if isinstance(value, unicode):
        m = POINT_RE.search(value)
        if m:
            a, b = m.group('lat'), m.group('lng')
        return float(a), float(b)
                    
class LocationWidget(forms.Textarea):
   
    def __init__(self, *args, **kw):

        self.map_width = kw.get("map_width", DEFAULT_WIDTH)
        self.map_height = kw.get("map_height", DEFAULT_HEIGHT)

        super(LocationWidget, self).__init__(*args, **kw)
        self.inner_widget = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):

        if value is None:
            locator = 'true'
            lat, lng = point_to_latlng(DEFAULT_EWKT)
            ewkt = DEFAULT_EWKT
        else:
            locator = 'false'
            if isinstance(value, unicode):
                lat, lng = point_to_latlng(value)
                ewkt = value
            else:
                lat, lng = point_to_latlng(unicode(value.ewkt))
                ewkt = value.ewkt
        js = '''
<script type="text/javascript">
//<![CDATA[


    var map_%(name)s;
    var click_%(name)s;
    var map_locator_%(name)s = %(locator)s
    
    function savePosition_pan%(name)s(point)
    {
        savePosition_%(name)s(point)
        map_%(name)s.panTo(point);
    }
    function savePosition_%(name)s(point)
    {
        var input = document.getElementById("id_%(name)s");
        input.value = "SRID=4326;POINT(" + point.lng().toFixed(4) + " " + point.lat().toFixed(4) + ")";
    }
        
    function load_%(name)s() {
        
        var callback = function(currentLocation, supportedLocation, errorLocation, firstCallback) {
            if (supportedLocation && !errorLocation) {
                map_%(name)s.setCenter(currentLocation)
            }
            if (errorLocation==true && firstCallback==true ) {
                alert("Cannot find location.")
            }
            if (supportedLocation==false  && firstCallback==true) {
                alert("Finding location not supported.")
            }
        }
        if (map_locator_%(name)s) {
            getCurrentLocation(callback)
        }

        var options = {
            zoom: 13,
            center: new google.maps.LatLng(%(lat)f, %(lng)f),
            mapTypeId: google.maps.MapTypeId.ROADMAP
            // mapTypeControl: true,  
            // navigationControl: true
        };
        
        map_%(name)s = new google.maps.Map(document.getElementById("map_%(name)s"), options);

        var marker = new google.maps.Marker({
                map: map_%(name)s,
                position: new google.maps.LatLng(%(lat)f, %(lng)f),
                draggable: true
        
        });
        google.maps.event.addListener(marker, 'dragend', function(mouseEvent) {
            savePosition_%(name)s(mouseEvent.latLng);
        });

        function singleClick(mouseEvent) {
            marker.setPosition(mouseEvent.latLng);
            savePosition_pan%(name)s(mouseEvent.latLng);
        }
        
        google.maps.event.addListener(map_%(name)s, 'click', function(mouseEvent){
            click_%(name)s = 0
            var that = this
            setTimeout(function() {
                var dblclick = click_%(name)s
                if (dblclick > 0) {
                    click_%(name)s = dblclick-1
                } else {
                    singleClick.call(that, mouseEvent);
                }
            }, 300);
        });

        google.maps.event.addListener(map_%(name)s, 'dblclick', function(mouseEvent){
            click_%(name)s = 2
        });


    }
    
    $(document).ready(function(){
        load_%(name)s();
    });

//]]>
</script>
        ''' % dict(name=name, lat=lat, lng=lng, locator=locator)
        html = self.inner_widget.render("%s" % name, ewkt, dict(id='id_%s' % name))
        html += '<div id="map_%s" style="width: %dpx; height: %dpx"></div>' % (name, self.map_width, self.map_height)

        return mark_safe(js + html)

    class Media:
        js = (
            'http://maps.google.com/maps/api/js?sensor=false',
            'http://code.google.com/apis/gears/gears_init.js',
            'http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js',
            '%scarpool/getcurrentlocation.js' % settings.STATIC_URL
        )

class LocationFormField(GeometryField):
    widget = LocationWidget
    

class DateSelectWidget(forms.DateInput):

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.11/jquery-ui.min.js'
        )
        css = {'screen': ('http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.10/themes/south-street/jquery-ui.css',)}

    def render(self, name, value, *args, **kwargs):
        html = super(DateSelectWidget, self).render(name, value, *args, **kwargs)
        html += '''
<script type="text/javascript">
//<![CDATA[

    $(document).ready(function(){
        $("#id_%(name)s").datepicker({
            dateFormat: 'yy-mm-dd'
        });
    });

//]]>
</script>''' % dict(name=name)
        return mark_safe(html)    

class DateTimeSelectWidget(forms.DateTimeInput):

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.11/jquery-ui.min.js',
            '%scarpool/jquery-ui-timepicker-addon.js' % settings.STATIC_URL
        )
        css = {
            'screen': (
                'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.10/themes/south-street/jquery-ui.css',
                '%scarpool/jquery-ui-timepicker-addon.css' % settings.STATIC_URL
            )
        }

    def render(self, name, value, *args, **kwargs):
        html = super(DateTimeSelectWidget, self).render(name, value, *args, **kwargs)
        html += '''
<script type="text/javascript">
//<![CDATA[

    $(document).ready(function(){
        $("#id_%(name)s").datetimepicker({
            timeFormat: 'h:mm:ss',
            dateFormat: 'yy-mm-dd'
        });
    });

//]]>
</script>''' % dict(name=name)
        return mark_safe(html)
        
class TimeSelectWidget(forms.TimeInput):

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.11/jquery-ui.min.js',
            '%scarpool/jquery-ui-timepicker-addon.js' % settings.STATIC_URL
        )
        css = {
            'screen': (
                'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.10/themes/south-street/jquery-ui.css',
                '%scarpool/jquery-ui-timepicker-addon.css' % settings.STATIC_URL
            )
        }
        
    def render(self, name, value, *args, **kwargs):
        html = super(TimeSelectWidget, self).render(name, value, *args, **kwargs)
        html += '''
<script type="text/javascript">
//<![CDATA[

    $(document).ready(function(){
        $("#id_%(name)s").timepicker({
            timeFormat: 'h:mm:ss'
        });
    });

//]]>
</script>''' % dict(name=name)
        return mark_safe(html)    
    