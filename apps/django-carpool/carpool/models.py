from django.contrib.gis.db import models

class Trip(models.Model):
    email = models.EmailField()
    from_point = models.PointField()
    to_point = models.PointField()
    when = models.DateTimeField()
    
    objects = models.GeoManager()
