import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from messages.models import Thread, DirectMessage
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification
from django.template.defaultfilters import date as date_filter
from django.utils import timezone

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.thread_group_name = f'thread_{self.thread_id}'
        
        # Join thread group
        await self.channel_layer.group_add(
            self.thread_group_name,
            self.channel_name
        )
        
        # Validate user belongs to thread
        is_member = await self.is_thread_member()
        if not is_member:
            await self.close()
            return
        
        await self.accept()
        
        # Mark messages as read
        await self.mark_messages_read()
    
    async def disconnect(self, close_code):
        # Leave thread group
        await self.channel_layer.group_discard(
            self.thread_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']
        
        # Save message to database
        message = await self.save_message(message_content)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.thread_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message['id'],
                    'content': message['content'],
                    'sender_id': message['sender_id'],
                    'sender_username': message['sender_username'],
                    'sender_avatar': message['sender_avatar'],
                    'timestamp': message['timestamp'],
                    'timestamp_formatted': message['timestamp_formatted']
                }
            }
        )
        
        # Create notifications for other participants
        for user_id in message['other_participants']:
            await self.create_notification(user_id, message['id'])
    
    async def chat_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))
    
    @database_sync_to_async
    def is_thread_member(self):
        try:
            thread = Thread.objects.get(id=self.thread_id)
            return thread.participants.filter(id=self.user.id).exists()
        except Thread.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        thread = Thread.objects.get(id=self.thread_id)
        message = DirectMessage.objects.create(
            thread=thread,
            sender=self.user,
            content=content
        )
        message.read_by.add(self.user)
        
        # Update thread timestamp
        thread.save()  # This updates the 'updated_at' field
        
        # Get other participants for notifications
        other_participants = list(
            thread.participants.exclude(id=self.user.id).values_list('id', flat=True)
        )
        
        return {
            'id': message.id,
            'content': message.content,
            'sender_id': self.user.id,
            'sender_username': self.user.username,
            'sender_avatar': self.user.profile.avatar.url if hasattr(self.user, 'profile') and self.user.profile.avatar else '/static/images/default-avatar.png',
            'timestamp': message.created_at.isoformat(),
            'timestamp_formatted': date_filter(message.created_at, "M d, Y, g:i a"),
            'other_participants': other_participants
        }
    
    @database_sync_to_async
    def create_notification(self, recipient_id, message_id):
        try:
            recipient = User.objects.get(id=recipient_id)
            thread = Thread.objects.get(id=self.thread_id)
            
            notification = Notification.objects.create(
                recipient=recipient,
                sender=self.user,
                notification_type='message',
                content_type=ContentType.objects.get_for_model(thread),
                object_id=thread.id
            )
            
            # Send notification to user's notification group
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            
            channel_layer = get_channel_layer()
            notification_group_name = f'notifications_{recipient_id}'
            
            async_to_sync(channel_layer.group_send)(
                notification_group_name,
                {
                    'type': 'notification_message',
                    'notification': {
                        'id': notification.id,
                        'sender': self.user.username,
                        'sender_avatar': self.user.profile.avatar.url if hasattr(self.user, 'profile') and self.user.profile.avatar else '/static/images/default-avatar.png',
                        'type': 'message',
                        'created_at': date_filter(notification.created_at, "M d, Y, g:i a"),
                        'thread_id': self.thread_id
                    }
                }
            )
            
            # Update unread count
            count = Notification.objects.filter(recipient=recipient, read=False).count()
            async_to_sync(channel_layer.group_send)(
                notification_group_name,
                {
                    'type': 'unread_count_message',
                    'count': count
                }
            )
            
            return notification.id
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def mark_messages_read(self):
        thread = Thread.objects.get(id=self.thread_id)
        unread_messages = thread.messages.exclude(sender=self.user).exclude(read_by=self.user)
        
        for message in unread_messages:
            message.read_by.add(self.user)