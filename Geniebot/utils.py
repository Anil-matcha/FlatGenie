import facebook
import decimal, time, os, requests
import googlemaps
from .models import *
from difflib import SequenceMatcher
from math import radians, cos, sin, asin, sqrt
gmaps = googlemaps.Client(key='AIzaSyA4glo9I2hBgJEKee_GritAwCr8fuvC4hs')
daily_flats = []

f = open('search_locations')
fo = open('all_location')
fw = open('unknown messages', 'w')
lines = [x.strip() for x in f.readlines()]
lineso = [x.strip() for x in fo.readlines()]

amenities = ["fridge", "washing machine", "tv", "wifi", "sofa", "dining table", "gas stove", "geyser", "power backup", "lift", "gym", "internet", "maid", "cook", "swimming pool"]
location = []

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def store_flat_data(post):
    fbid = post['id']
    try:
        message = post['message']
    except:
        return
    
    try:
        attachments = post['attachments']
    except:
        print("No attachments", post.keys(), fbid)
    
    if(Flat.objects.filter(fbid=fbid).count()!=0):
        print("Flat data already exists")
        return    
    
    matching_word, matching_location, similarity, index = check_location(message)
    if(similarity<0.75):
        fw.write(message)
        return

    print("location data", matching_location, lineso[index])
    location = Location.objects.get(name=lineso[index])
    flat = Flat.objects.create(fbid=fbid, location=location)
    
    try:
        image_url = attachments['data'][0]['subattachments']['data'][0]['media']['image']['src']
    except:
        image_url = "https://scontent.fblr1-2.fna.fbcdn.net/v/t1.0-9/18813663_241032179715836_7082794106048982309_n.png?oh=cd305a42c1f5f81a21aa032370f36ed6&oe=59DBB23B"
        
    flat.image_url = image_url    
    
    if("female" in message.lower()):
        gender = 0
    elif("male" in message.lower()):
        gender = 1
    else:
        gender = 2
    
    flat.gender = gender
    
    if("bhk" in message.lower()):
        index = message.lower().find("bhk")
        for i in range(index-1, -1, -1):
            try:
                num_of_rooms = int(message[i])
                flat.num_of_rooms = num_of_rooms
                break
            except:
                print("Number of bhk not mentioned")
    
    if("₹" in message):
        price = ''
        index = message.find("₹")
        for i in range(index+1, len(message)):
            if(message[i]==' ' or message[i]=='\n' or message[i]=='\t'):
                break
            else:
                price = price + message[i]
                
        price = price.replace(',', '')
                
        try:        
            price = int(price)    
            flat.rent = price
        except:
            print("Not able to parse")
            a = 1
    else:
        if("rent" in message.lower()):
            index = message.lower().find("rent")
            start = False
            price = ''
            for i in range(index+4, len(message)):
                if(not start):
                    try:
                        n = int(message[i])
                        start = True
                    except:
                        a = 1
                else:
                    if(message[i]==' ' or message[i]=='\n' or message[i]=='\t'):
                        break
                    else:
                        price = price + message[i]
                        
                price = price.replace(',', '')
                
        try:        
            price = int(price)
            flat.rent = price
        except:
            print("Not able to parse")
            a = 1                
              
    amenities_present = ", ".join([x for x in amenities if x in message.lower()])
    flat.amenities = amenities_present
                    
    if("deposit" in message.lower()):
        index = message.find("deposit")
        if("k" in message[index+7:index+15]):
            k_index = message[index+7:index+15].find("k")
            deposit = ""
            for i in range(k_index, index+7, -1):
                if(message[i]==' ' or message[i]=='\n' or message[i]=='\t'):
                    break
                else:
                    try:
                        j = int(message[i])
                        deposit = message[i] + deposit 
                    except:
                        break
            try:
                deposit = int(deposit)*1000
                flat.deposit = deposit
            except:
                a=1
                
        elif("/-" in message[index+7:index+15]): 
            end_index = message[index+7:index+15].find("/-")
            deposit = ""
            for i in range(end_index, index+7, -1):
                if(message[i]==' ' or message[i]=='\n' or message[i]=='\t'):
                    break
                else:
                    try:
                        j = int(message[i])
                        deposit = message[i] + deposit 
                    except:
                        break
            try:
                flat.deposit = deposit
                deposit = int(deposit)*1000
            except:
                a=1
                
                
        elif(":" in  message[index+7:index+15]):
            deposit = ""
            start = False
            for i in range(index+7, index+15):
                if(not start):
                    try:
                        int(message[i])
                        start = True
                        deposit = deposit + message[i]
                    except:
                        a = 1
                else:
                    if(message[i]==' ' or message[i]=='\n' or message[i]=='\t'):
                        break

            try:
                flat.deposit = deposit
                deposit = int(deposit)
            except:
                a=1                   
    
    try:
        existing_flat = Flat.objects.get(location=location, rent=flat.rent, amenities=flat.amenities, deposit=flat.deposit, gender=flat.gender)
        print("Duplicate listing", existing_flat.fbid, flat.fbid)        
        flat.delete()
    except:
        daily_flats.append(flat)
        flat.save()            

def check_location(message):
    #print(message)
    words = message.split()
    similarity = 0
    index = -1
    for word in words:
        for i, location in enumerate(lines):
            new_similarity = similar(word.lower(), location.lower())
            if(new_similarity>similarity):
                matching_word = word
                matching_location = location
                similarity = new_similarity
                index = i
                
    return matching_word, matching_location, similarity, index

def test_paginate_facebook(pagequery):
    count, matching_count = 0, 0
    while(count<100):
        r = requests.get(pagequery)
        response = r.json()
        all_posts = response['data']
        for post in all_posts:
            if("message" in post):
                 matching_word, matching_location, similarity, index = check_location(post["message"])
                 print(matching_word, matching_location, similarity)
                 if(similarity>0.75):
                     matching_count = matching_count + 1
                 else:
                     fw.write(post["message"])
            else:
                print(post.keys())
            count = count + 1
        pagequery = response['paging']['next']
        print(count, matching_count, (matching_count*100.0)/count)
        time.sleep(5)
            
def paginate_facebook(pagequery):
    while(Flat.objects.all().count()<1000):
        r = requests.get(pagequery)
        response = r.json()
        all_posts = response['data']
        for post in all_posts:
            store_flat_data(post)
        pagequery = response['paging']['next']
    
def get_distance(lat1, lng1, lat2, lng2):
    return (lat1-lat2)**2+(lng1-lng2)**2
    
def get_location(location):
    # Geocoding an address
    geocode_result = gmaps.geocode(location + ' Bangalore')
    lat = decimal.Decimal(geocode_result[0]['geometry']['location']['lat'])
    lng = decimal.Decimal(geocode_result[0]['geometry']['location']['lng'])
    return lat, lng
    
def get_haversine_distance(lat1, lng1, lat2, lng2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    # haversine formula 
    dlng = lng2 - lng1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km
    
def get_flats_by_location_and_rate(lat, lng, rent, index):
    print(lat, lng)
    flats = Flat.objects.filter(rent__gte=rent-2000, rent__lte=rent+2000).prefetch_related("location")
    all_flats, distance = [], []
    for flat in flats:
        num_km = get_haversine_distance(flat.location.lat, flat.location.lng, lat, lng)
        #print(num_km, flat.location.lat, flat.location.lng, lat, lng)
        if(num_km < 5):
            all_flats.append(flat)
            distance.append(num_km)
    
    for i in range(len(all_flats)-1):
        for j in range(i, len(all_flats)-1):
            if(distance[j]>distance[j+1]):
                temp = distance[j]
                distance[j] = distance[j+1]
                distance[j+1] = temp
                temp = all_flats[j]
                all_flats[j] = all_flats[j+1]
                all_flats[j+1] = temp
                      
                      
    if(10*index>len(all_flats)-1):
        return [], []
    else:
        if(10*(index+1)>(len(all_flats)-1)):
            start, end = 10*index, len(all_flats)
        else:
            start, end = 10*index, 10*(index+1)
            
    return all_flats[start:end], distance
    
def get_flats_by_location(lat, lng):
    print(lat, lng)
    all_flats, distance = [], []
    for flat in daily_flats:
        num_km = get_haversine_distance(flat.location.lat, flat.location.lng, lat, lng)
        #print(num_km, flat.location.lat, flat.location.lng, lat, lng)
        if(num_km < 5):
            all_flats.append(flat)
            distance.append(num_km)
    
    for i in range(len(all_flats)-1):
        for j in range(i, len(all_flats)-1):
            if(distance[j]>distance[j+1]):
                temp = distance[j]
                distance[j] = distance[j+1]
                distance[j+1] = temp
                temp = all_flats[j]
                all_flats[j] = all_flats[j+1]
                all_flats[j+1] = temp
                      
                      
    if(10*index>len(all_flats)-1):
        return [], []
    else:
        if(10*(index+1)>(len(all_flats)-1)):
            start, end = 10*index, len(all_flats)
        else:
            start, end = 10*index, 10*(index+1)
            
    return all_flats[start:end], distance    
    
    
def make_flats_carousel(flats, distance):    
    attachment = {'type' : 'template'}
    payload = {'template_type' : 'generic'}#, "top_element_style": "compact"}
    elements = []
    length = len(flats)
    for i in range(0, length):
        flat = flats[i]
        new_element = {}
        title = 'Located in '+flat.location.name+ "\nRent : "+str(flat.rent)
        subtitle = "Distance : "+str(distance[i])[0:3]+" km"#+"\nDeposit : "+flat.deposit+"\nRooms : "+flat.num_of_rooms+"bhk"
        new_element['title'] = title
        new_element['subtitle'] = subtitle
        new_element['image_url'] = flat.image_url
        new_element["default_action"] = {
            "type": "web_url",
            "url": "https://www.facebook.com/"+flat.fbid,
            "messenger_extensions": True,
            "webview_height_ratio": "tall",
            "fallback_url": "https://www.facebook.com/"+flat.fbid
        }
        elements.append(new_element)
    payload['elements'] = elements
    attachment['payload'] = payload
    message = {'attachment': attachment}
    return message    