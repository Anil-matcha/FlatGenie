from .utils import *
from .views import *
import facebook
from django.db.models import Q
from my_django_projects.celery import app
from celery.schedules import crontab
from celery.decorators import periodic_task, task

def update_flats_data():
    graph = facebook.GraphAPI(access_token='EAAF47rOwYZC4BABZBK1cv2TXKFY9Gtng0Knoe4LbIOaozQk8qEl4zFx51bt1SqLZAZCl55oLWtY0oqQfbzhh2JbEajtZADfZAAx3fJkbiGB2xzrcjatjTvJS77j6ov1aAlvrA9ACaIj5E0HSn0LeRGdF2ennDPup5zScuwd0puJQZDZD', version='2.7')
    response = graph.get_object("263827920387171/feed", fields='message,attachments')
    all_posts = response['data']
    for post in all_posts:
        store_flat_data(post)
    paginate_facebook(response['paging']['next'])
    
def notify_users():
    all_subscriptions = User_Subscription.objects.all()
    for subscription in all_subscriptions:
        lat, lng = get_location(subscription.location_name)
        all_flats, distance = get_flats_by_location(lat, lng)
        paging_context[fbid] = 0
        message = make_flats_carousel(all_flats, distance)
        replies = ['next', 'change location', 'change rent']
        quick_replies = []
        for reply in replies:
            new_reply = {'content_type':'text', 'title':reply, 'payload':reply}
            quick_replies.append(new_reply)
        message['quick_replies'] = quick_replies    
        response_msg = json.dumps({"recipient":{"id":subscription.fbid}, "message":message})
        status = requests.post(Post_Message_Url, headers={"Content-Type": "application/json"}, data=response_msg)        
        
        send_text_message(subscription.fbid, "New flats near "+subscription.location_name)
        
@periodic_task(run_every=(crontab(minute=0, hour=0)))        
def clear_daily_cache():
    paging_context = {}
    daily_flats = []