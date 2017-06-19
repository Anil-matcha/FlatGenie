from django.db import models

GENDER_TYPE_CHOICES = (
    (0, 'Male'),
    (1, 'Female'),
    (2, 'Any'),
)

class Location(models.Model):
    name = models.CharField(max_length=100, blank=True, default='default')
    lat = models.DecimalField(max_digits=9, decimal_places=5)
    lng = models.DecimalField(max_digits=9, decimal_places=5)

# Create your models here.
class Flat(models.Model):
    rent = models.IntegerField(default=0)
    location = models.ForeignKey(Location, related_name='flat', on_delete=models.CASCADE, null=True)    
    gender = models.IntegerField(choices=GENDER_TYPE_CHOICES, null=True)
    deposit = models.IntegerField(default=0)
    num_of_rooms = models.IntegerField(default=0)
    amenities = models.TextField(blank=True)
    fbid = models.TextField(blank=True)
    image_url = models.TextField(null=True)
    
class User_Subscription(models.Model):
    fbid = models.TextField(blank=True)
    location_name = models.TextField(blank=True)