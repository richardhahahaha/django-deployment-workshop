# -*- coding: utf-8 -*-
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

class Trip(models.Model):
    email = models.EmailField(verbose_name=_('Email'))
    travel_path = models.LineStringField(verbose_name=_('Route'), srid=4326)
    when = models.DateTimeField(verbose_name=_('When'))
    
    objects = models.GeoManager()
