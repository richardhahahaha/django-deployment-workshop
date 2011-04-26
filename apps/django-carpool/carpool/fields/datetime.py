from django import forms
from django.db import models
from django.utils.safestring import mark_safe
from django.conf import settings

JQUERY_JS = getattr(settings, 'JQUERY_JS', 'http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js')
JQUERY_UI_JS = getattr(settings, 'JQUERY_UI_JS', 'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.11/jquery-ui.min.js')
JQUERY_UI_CSS  = getattr(settings, 'JQUERY_UI_CSS', 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.10/themes/south-street/jquery-ui.css')

class DateSelectWidget(forms.DateInput):

    class Media:
        js = (
            JQUERY_JS,
            JQUERY_UI_JS
        )
        css = {'screen': (JQUERY_UI_CSS,)}

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
            JQUERY_JS,
            JQUERY_UI_JS,
            '%scarpool/jquery-ui-timepicker-addon.js' % settings.STATIC_URL
        )
        css = {
            'screen': (
                JQUERY_UI_CSS,
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
            JQUERY_JS,
            JQUERY_UI_JS,
            '%scarpool/jquery-ui-timepicker-addon.js' % settings.STATIC_URL
        )
        css = {
            'screen': (
                JQUERY_UI_CSS,
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
    