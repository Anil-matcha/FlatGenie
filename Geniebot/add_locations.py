import googlemaps
import decimal, time
gmaps = googlemaps.Client(key='')
from .models import *

def store_locations():
    Location.objects.all().delete()
    f = open("all_location")
    lines = f.readlines()
    
    for line in lines:
        # Geocoding an address
        geocode_result = gmaps.geocode(line + ' Bangalore')
        lat = decimal.Decimal(geocode_result[0]['geometry']['location']['lat'])
        lng = decimal.Decimal(geocode_result[0]['geometry']['location']['lng'])
        name = geocode_result[0]['address_components'][0]['short_name']
        
        Location.objects.create(name=name, lat=lat, lng=lng)
        print(name)
        time.sleep(2)
        
    f.close()
    
def update_location_names():
    f = open("all_location")
    lines = f.readlines()
    all_locations = Location.objects.all()
    id_0 = all_locations[0].id
    for location in all_locations:
        location.name = lines[location.id - id_0].strip()
        location.save()
    f.close()