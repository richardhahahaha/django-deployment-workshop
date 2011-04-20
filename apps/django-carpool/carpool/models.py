# -*- coding: utf-8 -*-
from django.contrib.gis.db import models

class Trip(models.Model):
    email = models.EmailField(verbose_name="Epost")
    from_point = models.PointField(verbose_name="Fra", srid=4326)
    to_point = models.PointField(verbose_name="Til", srid=4326)
    when = models.DateTimeField(verbose_name="Når")
    
    objects = models.GeoManager()
