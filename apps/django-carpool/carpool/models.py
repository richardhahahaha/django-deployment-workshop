# -*- coding: utf-8 -*-
from django.contrib.gis.db import models

class Trip(models.Model):
    email = models.EmailField(verbose_name="Epost")
    from_point = models.PointField(verbose_name="Fra")
    to_point = models.PointField(verbose_name="Til")
    when = models.DateTimeField(verbose_name="Når")
    
    objects = models.GeoManager()
