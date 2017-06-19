# FlatGenie

# Chatbot built for Bots for good challenge

# Inspiration
One of my flatmates was vacating the flat 1 month ago and we had to find a new flatmate in a short span.The main source of finding flatmates in facebook group https://www.facebook.com/groups/FlatsandFlatmatesBangaloreChapter/. So we posted a detailed story describing the flat and its details and was expecting a good response.

But then I saw that finding a flatmate through the facebook group is quite inefficient. There are quite a lot of people posting in the group and the post quickly gets old and dead. Also for any user trying to find a flat nearby his location its quite a task to go through all the posts to catch the posts of his interest. 

When I came across this competition I immediately felt this would be a great problem to solve using a facebook chatbot and started working on it.  

# What it does
The bot fetches all the facebook posts in https://www.facebook.com/groups/FlatsandFlatmatesBangaloreChapter/ using facebook graph api. After fetching the data all important details are identified from the text of the post and stored structurally in the database. 

The user can filter for posts based on the location and his rent limit.A carousel of flats are displayed. If he is interested in any post he can click on it to view the full details. If he is not interested he can go to the next set of posts or change location and rent if required.

Also user can set a reminder so that he gets an alert message when a new post of his interest is added.This way whoever needs a flat can just set a reminder and need not worry about checking at repeated intervals to find the facebook post of his interest.

## How we built it
We use django with python for server which gets the webhook request from facebook messenger. We used api.ai for NLP to parse the conversation and find context of the sentence to respond to.

## Challenges we ran into
The main challenge was extracting the flat info from the facebook post. What we observed is that the posts are unstructured so we have to take into consideration many things to get the correct info. For example rent might be mentioned as **6k, 6000 ₹6000** etc. Deposit also in a similar way and both of them shouldn't be confused with each other. Similarly flatmate gender needs to be found out. 

Number of rooms in the flat needs be found out whether 1bhk, 2bhk, 3bhk etc. Here also the data isn't proper. Sometimes its 2bhk sometimes its  2 bhk(extra space in between).Also the amenities inside the house such as fridge, washing machine etc. needs to be parsed out.

The main issue was with finding the location inside the sentence.Here no principle can be applied to get the location in the sentence. Since the facebook group belongs to bangalore we fetched a list of all the famous places in bangalore and stored them. Then we had to do a similarity match from all words in the facebook post with all locations available.The max matching word was taken if matching % is greater than 75. We used the above method to find location and we were able to find location in 92% of the posts. 

When the user types a location we need to display all the nearby flats . So we got the latitude, longitude of the user input location and also stored the latittude, longitude of the location inside the facebook post. Then we have to query on the database to get all the nearby places which was a complex task. We used Haversine formula to get the distance and then present the data in a list.

## Accomplishments that we're proud of
We were not aware of how or what a chatbot does initially when we signed up for the competition. We don't know what technologies to use or what is the procedure to follow to develop a chatbot. We weren't well versed with NLP 
or chatbot ux which needs to be developed. But we started learning everything one step at a time. We read the basics of NLP, chatbot ux, facebook messenger api etc. 

Initially we tested waters with wit.ai for NLP but we had issues with it identifying the rent value from the conversation. We were doing things on it for quite some time but it didn't work out. Half the time was over and we hit a wall. But we didn't give up. 

We quickly read on what other alternatives are available and what might be a correct fit. We found api.ai to be a correct fit and we immediately switched and got things working fast by working relentlessly. Now api.ai was handling the conversation and it needs to fetch the data from the server to display for the user. Again there was an issue here since api.ai doesn't pass the facebook id to the backend server. We tried to find a solution but found there is none except hosting it yourself. So we quickly moved to our own hosting, now api.ai is used only to get the context from the user reply. Rest all the things and sending reply, info are handled by backend server.

Also we needed an option to support paging to get the next set of data if user wants more. Again we tried to find a solution online but got to know no such support is available. So we have build in-house support for paging.

Whenever we had an issue we could have given up but instead we started thinking what can be done to resolve the issue. Should we switch to another framework? Is there any solution for the problem mentioned above online which is currently supported? Should we find a way to build an in-house solution . We asked us these questions continuously and found all it needs is putting a step forward and trying things to make it work rather than thinking forever/cusring luck. 

These all are great accomplishments to be proud of.

## What we learned
The foremost thing we found out was the world is fast changing to go to a new platform i.e the conversational space away from websites and apps. People now a days are spending more time on chatting platforms rather than apps/websites. And user time=money. 

Also chatting apps doesn't mean they support only one thing i.e chatting. Now entire world is being provided in it. Best example is the massive popularity of Wechat . The sheer amount of time people spending on the app is mind-boggling. And Wechat has introduced a lot of features inside the app such as money transaction, taking food order etc. With its success its assured that messengers are the next wave of technology and we should be prepared for that.

Adding to the above we got to learn what are the concepts of AI, NLP in processing a conversation. What are the building blocks of a sentence and how to identify key words inside the sentence. How to maintain the context in a conversation so that we know what the user wants in a chat flow. 

We learned what are the features supported by facebook messenger for a chatbot. How to design a chatbot, what are the principles to be followed to make the process easier for a user, what are the ui elements supported by facebook messenger and where to use them in a proper way.

Also learnt facebook graph api to get all the facebook posts for the data.

## What's next for FlatGenie bot
Currently FlatGenie supports Bengaluru but in future it can be extended to other cities as well. More filters can be added to customize the query according to user interest.  Also data parsing and conversation can be made more robust. 

The idea is a generic one, take data from a facebook group to solve the problem of finding the correct post. This can be applied to other facebook groups as well such as BuySellTickets where one can find tickets. Local market groups for selling second hand products etc. The possibilities are limitless
