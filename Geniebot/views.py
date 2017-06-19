from django.shortcuts import render

# Create your views here.
import json, requests, random, re
from pprint import pprint
 
from django.views import generic
from django.http.response import HttpResponse
 
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .utils import *
ACCESS_TOKEN = ''
Post_Message_Url = 'https://graph.facebook.com/v2.6/me/messages?access_token='+ACCESS_TOKEN
api_ai_url = 'https://api.api.ai/api/query/'
query_data = {}
query_data['v'] = '20150910'
query_data['lang'] = 'en'
headers = {'Authorization': 'Bearer '}
paging_context = {}
 
def add_fb_menu():
    persistent_menu = []
    menu_en = {"locale":"default", "composer_input_disabled":True}
    call_to_actions = []
    call_to_action_location = {"title" : "Find me a flat", "type" : "postback", "payload" : "LOCATION"} 
    call_to_actions.append(call_to_action_location)
    menu_en['call_to_actions'] =  call_to_actions
    persistent_menu.append(menu_en)
    message = {"persistent_menu" : persistent_menu}
    Menu_Post_Message_Url = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+ACCESS_TOKEN   
    status = requests.post(Menu_Post_Message_Url, headers={"Content-Type": "application/json"}, data=message)    
    pprint(status.json())

def handle_postback(fbid, postback):
    if(postback=='PAYLOAD_LOC'):
        query_data['query'] = 'Hello'
        query_data['sessionId'] = fbid 
        r = requests.get(api_ai_url, headers=headers, params=query_data)        
        send_text_message(fbid, "What is your preferred location ?")        
    elif(postback=='FACEBOOK_WELCOME'):    
        send_response(fbid, "Hello")
    elif(postback=='PAYLOAD_SUB'):    
        send_response(fbid, "Manage subscription")
        handle_subscription_intent(fbid, {})        
 
def welcome_query(sessionId):
    query_data['query'] = 'hello'
    query_data['sessionId'] = sessionId 
    r = requests.get(api_ai_url, headers=headers, params=query_data)

def handle_location_intent(fbid, data):
    message = {}
    replies = ['4k', '6k', '8k', '10k', '12k', '14k', '16k', '18k', '20k']
    quick_replies = []
    for reply in replies:
        new_reply = {'content_type':'text', 'title':reply, 'payload':reply}
        quick_replies.append(new_reply)
    message['quick_replies'] = quick_replies
    message['text'] = 'Cool\nWhat is your preferred budget ?'
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":message})
    status = requests.post(Post_Message_Url, headers={"Content-Type": "application/json"}, data=response_msg)

def handle_change_location(fbid):
    send_text_message(fbid, "Sure, What is your preferred location ?")
    
def handle_change_rent(fbid):    
    handle_location_intent(fbid, {})

def handle_paging_intent(fbid, data):
    try:
        params = data['result']['contexts'][-1]['parameters']
        location, rent, paging = params['location'], params['Rent'], params['paging_entity']
    except:
        print("Exception in paging intent")
        return
    print("paging intent", location, rent, paging)
    if('k' in rent):
        rent = rent.replace('k', '')
        rent = int(rent)*1000
    lat, lng = get_location(location)
    if(paging=='next'):
        paging_context[fbid] = paging_context[fbid] + 1
    elif(paging=='prev'):
        paging_context[fbid] = paging_context[fbid] - 1
    elif(paging=='change location'):
        paging_context[fbid] = 0
        handle_change_location(fbid)
        return
    elif(paging=='change rent'):
        paging_context[fbid] = 0        
        handle_change_rent(fbid)        
        return
    
    flats, distance = get_flats_by_location_and_rate(lat, lng, rent, paging_context[fbid])    
    message = make_flats_carousel(flats, distance)
    if(paging_context[fbid]==0):
        replies = ['next', 'change location', 'change rent']
    else:
        replies = ['next', 'prev', 'change location', 'change rent']        
    quick_replies = []
    for reply in replies:
        new_reply = {'content_type':'text', 'title':reply, 'payload':reply}
        quick_replies.append(new_reply)
    message['quick_replies'] = quick_replies    
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":message})
    status = requests.post(Post_Message_Url, headers={"Content-Type": "application/json"}, data=response_msg)

def handle_rent_intent(fbid, data):
    try:
        location, rent = data['result']['contexts'][-1]['parameters']['location'], data['result']['contexts'][-1]['parameters']['Rent']
    except:
        return
    print("Rent intent", location, rent)
    if('k' in rent):
        rent = rent.replace('k', '')
        rent = int(rent)*1000
    lat, lng = get_location(location)
    flats, distance = get_flats_by_location_and_rate(lat, lng, rent, 0)
    paging_context[fbid] = 0
    message = make_flats_carousel(flats, distance)
    
    replies = ['next', 'change location', 'change rent']
    quick_replies = []
    for reply in replies:
        new_reply = {'content_type':'text', 'title':reply, 'payload':reply}
        quick_replies.append(new_reply)
    message['quick_replies'] = quick_replies    
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":message})
    status = requests.post(Post_Message_Url, headers={"Content-Type": "application/json"}, data=response_msg)

def handle_welcome_intent(fbid, data):
    send_text_message(fbid, "Greetings! I am Genie bot, I can help you with finding a flat for nearby.")
    send_image_message(fbid, "http://38.media.tumblr.com/98d2ed667e32b929532cc3ac3b9e4c8f/tumblr_na61k0Tgh61qj1tqqo10_500.gif")
    send_text_message(fbid, "\nWhich location do you prefer?")    

def handle_subscription_intent(fbid, data):
    print("Subscription intent")
    send_text_message(fbid, "What location do you prefer?")

def subscribe_user(fbid, location):
    try:
        user_subscription = User_Subscription.objects.get(fbid=fbid)
        user_subscription.location_name = location
    except:
        User_Subscription.objects.create(fbid=fbid, location_name=location)

def handle_location_subscription_intent(fbid, data):
    try:
        location = data['result']['contexts'][-1]['parameters']['location']    
    except:
        return
    subscribe_user(fbid, location)
    send_text_message(fbid, "Sure, \nWill get you notified of any posts for location " + location)
    
def send_response(fbid, received_message):
    print(fbid, received_message)
    query_data['query'] = received_message
    query_data['sessionId'] = fbid 
    r = requests.get(api_ai_url, headers=headers, params=query_data)
    data = r.json()
    if(data['result']['metadata']['intentName']=='@location_intent'):
        handle_location_intent(fbid, data)
    elif(data['result']['metadata']['intentName']=='@rent_intent'):
        handle_rent_intent(fbid, data)
    elif(data['result']['metadata']['intentName']=='@paging_intent'):
        handle_paging_intent(fbid, data)
    elif(data['result']['metadata']['intentName']=='welcome_intent'):
        handle_welcome_intent(fbid, data)
    elif(data['result']['metadata']['intentName']=='@location_subscription_intent'):
        handle_location_subscription_intent(fbid, data)       
    else:
        messages = data['result']['fulfillment']['messages']
        for message in messages:
            if('speech' in message):
                send_text_message(fbid, message['speech'])
            elif('imageUrl' in message):
                send_image_message(fbid, message['imageUrl'])
                
def send_text_message(fbid, message): 
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":message}})
    status = requests.post(Post_Message_Url, headers={"Content-Type": "application/json"}, data=response_msg)

def send_image_message(fbid, image_url): 
    image_message = {"attachment":{"type":"image","payload":{"url":image_url}}}
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":image_message})
    status = requests.post(Post_Message_Url, headers={"Content-Type": "application/json"}, data=response_msg)    

class jokebot(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == 'james':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
        
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)
 
 
    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        #print(incoming_message)
        for entry in incoming_message['entry']:
            for message in entry['messaging']: 
                if 'message' in message: 
                    send_response(message['sender']['id'], message['message']['text'])  
                elif 'postback' in message:
                    handle_postback(message['sender']['id'], message['postback']['payload'])
        return HttpResponse()