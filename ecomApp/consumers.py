from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    # Called when the WebSocket connection is established
    async def connect(self):
        self.group_name = "order_notifications"  # Name of the group to subscribe to
        await self.channel_layer.group_add(self.group_name, self.channel_name)  # Add this channel to the group
        await self.accept()  # Accept the WebSocket connection

    # Called when the WebSocket connection is closed
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)  # Remove from group

    # Optional: Handle messages received from WebSocket client (not used here)
    async def receive(self, text_data):
        pass

    # Called when a message is sent to the group
    async def send_notification(self, event):
        # Send the message to the WebSocket client
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))