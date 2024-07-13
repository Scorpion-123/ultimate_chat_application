import django
django.setup()

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from .models import *
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

class ChatroomConsumer(WebsocketConsumer):
    
    def connect(self):
        self.user = self.scope['user']
        self.group_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.group = ChatGroup.objects.get(group_name = self.group_name)

        # After connecting, add the user to the selected group/chat-room.
        async_to_sync(self.channel_layer.group_add)(

            self.group_name,
            self.channel_name
        )

        # add and update online users.
        if self.user not in self.group.online_users.all():
            self.group.online_users.add(self.user)
            self.update_online_count()

        self.accept()


    def receive(self, text_data):

        text_data_json = json.loads(text_data)
        body = text_data_json['body']

        message = GroupMessage.objects.create(
            body = body,
            author = self.user,
            group = self.group
        )
        
        # This is the 'event' for the 'group_send' method.
        # The 'type' of the event will contain the 'event_handler' that is responsible for sending 'text_data'.
        event = {
            'type': 'message_handler',
            'message_id': message.id
        }  

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            event
        )


    def message_handler(self, event):
        message_obj_id = event['message_id']
        message_obj = GroupMessage.objects.get(id = message_obj_id)

        context = {
            'message': message_obj,
            'user': self.user
        }

        html = render_to_string('partials/chat_message_p.html', context)
        self.send(text_data = html)


    def disconnect(self, close_code):
        
        # This will remove the user with the specific channel name from the group/chat-room.
        async_to_sync(self.channel_layer.group_discard)(

            self.group_name,
            self.channel_name
        )

        # remove and update online users.
        if self.user in self.group.online_users.all():
            self.group.online_users.remove(self.user)
            self.update_online_count()
    

    def update_online_count(self):
        online_count = self.group.online_users.count() - 1
        
        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            event
        )

    
    def online_count_handler(self, event):
        count = event['online_count']

        context = {
            'online_count': count
        }
        html = render_to_string('partials/online_count.html', context)
        self.send(text_data = html)
    