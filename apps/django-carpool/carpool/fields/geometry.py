from django import forms
from django.utils.safestring import mark_safe
from django.contrib.gis.geos import *
from django.contrib.gis.forms.fields import GeometryField
from django.conf import settings

JQUERY_JS = getattr(settings, 'JQUERY_JS', 'http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js')
JQUERY_UI_JS = getattr(settings, 'JQUERY_UI_JS', 'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.11/jquery-ui.min.js')
JQUERY_UI_CSS  = getattr(settings, 'JQUERY_UI_CSS', 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.10/themes/south-street/jquery-ui.css')
CLASSY_JS = getattr(settings, 'CLASSY_JS', '%scarpool/classy.js' % settings.STATIC_URL)

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

get_current_location_js = '''
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
        
        gdgfields.utils.CurrentLocation.findLocation(callback)
'''

class LocationWidget(forms.Textarea):
   
    def __init__(self, *args, **kw):

        self.map_width = kw.get("map_width", DEFAULT_WIDTH)
        self.map_height = kw.get("map_height", DEFAULT_HEIGHT)

        super(LocationWidget, self).__init__(*args, **kw)
        self.inner_widget = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):

        if value is None:
            get_current_location = True
            lat, lng = point_to_latlng(DEFAULT_EWKT)
            ewkt = DEFAULT_EWKT
        else:
            get_current_location = False
            if isinstance(value, unicode):
                lat, lng = point_to_latlng(value)
                ewkt = value
            else:
                lat, lng = point_to_latlng(unicode(value.ewkt))
                ewkt = value.ewkt
                
        get_current_location = get_current_location and get_current_location_js % dict(name=name) or ''

        js = '''
<script type="text/javascript">
//<![CDATA[


    var map_%(name)s;
    var click_%(name)s;
    
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
        
        %(get_current_location)s

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
        
		var search_element = document.createElement('button')
		search_element.appendChild(document.createTextNode('Search'))
		search_element.type = 'button'
		search_element.index = 1;
  		map_%(name)s.controls[google.maps.ControlPosition.BOTTOM_LEFT].push(search_element);
  		
		var search_button = $(search_element).button()
		  		
  		var search_button_cb = function(item) {
  			map_%(name)s.panTo(item.location);
  		}
  		
  		search_button.click(function() {
  			new gdgfields.utils.LocationSearchPopup('%(name)s_popup', [])
  		})
  		
    }
    
    $(document).ready(function(){
        load_%(name)s();
    });

//]]>
</script>
        ''' % dict(name=name, lat=lat, lng=lng, get_current_location=get_current_location)
        html = self.inner_widget.render("%s" % name, ewkt, dict(id='id_%s' % name))
        html += '<div id="map_%s" style="width: %dpx; height: %dpx"></div>' % (
             name, self.map_width, self.map_height)

        return mark_safe(js + html)

    class Media:
        js = (
            'http://maps.google.com/maps/api/js?sensor=false',
            'http://code.google.com/apis/gears/gears_init.js',
            JQUERY_JS,
            JQUERY_UI_JS,
            CLASSY_JS,
            '%scarpool/getcurrentlocation.js' % settings.STATIC_URL,
            '%scarpool/getlocationfromadress.js' % settings.STATIC_URL,
        )

class LocationFormField(GeometryField):
    widget = LocationWidget

POLYLINE_RE = re.compile("SRID=\d+;POLYLINE\s?(\(\((?P<lng>\-?\d+\.\d+)\s(?P<lat>\-?\d+\.\d+)\)\))")

def polyline_to_latlng(value):
    if isinstance(value, unicode):
        m = POINT_RE.search(value)
        if m:
            a, b = m.group('lat'), m.group('lng')
        return float(a), float(b)
            
class DirectionsWidget(forms.Textarea):
   
    def __init__(self, *args, **kw):

        self.map_width = kw.get("map_width", DEFAULT_WIDTH)
        self.map_height = kw.get("map_height", DEFAULT_HEIGHT)

        super(LocationWidget, self).__init__(*args, **kw)
        self.inner_widget = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):

        if value is None:
            get_current_location = True
            lat, lng = point_to_latlng(DEFAULT_EWKT)
            lat_end, lng_end = None, None
            ewkt = DEFAULT_EWKT
        else:
            get_current_location = False
            if isinstance(value, unicode):
                polyline = polyline_to_latlng(value)
                lat, lng = polyline[0]
                lat_end, lng_end = polyline[-1]
                ewkt = value
            else:
                polyline = polyline_to_latlng(unicode(value.ewkt))
                lat, lng = polyline[0]
                lat_end, lng_end = polyline[-1]
                ewkt = value.ewkt
                
        get_current_location = get_current_location and get_current_location_js % dict(name=name) or ''

        js = '''
<script type="text/javascript">
//<![CDATA[


    var map_%(name)s;
    var click_%(name)s;
    
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
        
        %(get_current_location)s

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
        
		var search_element = document.createElement('button')
		search_element.appendChild(document.createTextNode('Search'))
		search_element.type = 'button'
		search_element.index = 1;
  		map_%(name)s.controls[google.maps.ControlPosition.BOTTOM_LEFT].push(search_element);
  		
		var search_button = $(search_element).button()
		  		
  		var search_button_cb = function(item) {
  			map_%(name)s.panTo(item.location);
  		}
  		
  		search_button.click(function() {
  			new gdgfields.utils.LocationSearchPopup('%(name)s_popup', [])
  		})
    }
    
    $(document).ready(function(){
        load_%(name)s();
    });

//]]>
</script>
        ''' % dict(name=name, lat=lat, lng=lng, get_current_location=get_current_location)
        html = self.inner_widget.render("%s" % name, ewkt, dict(id='id_%s' % name))
        html += '<div id="map_%s" style="width: %dpx; height: %dpx"></div>' % (
            name, self.map_width, self.map_height)

        return mark_safe(js + html)

    class Media:
        js = (
            'http://maps.google.com/maps/api/js?sensor=false',
            'http://code.google.com/apis/gears/gears_init.js',
            JQUERY_JS,
            JQUERY_UI_JS,
            CLASSY_JS,
            '%scarpool/getcurrentlocation.js' % settings.STATIC_URL,
            '%scarpool/getlocationfromadress.js' % settings.STATIC_URL
        )

class DirectionsFormField(GeometryField):
    widget = DirectionsWidget