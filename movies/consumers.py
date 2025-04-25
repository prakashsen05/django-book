import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Seat

class SeatAvailabilityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the theater ID from the URL
        self.theater_id = self.scope['url_route']['kwargs']['theater_id']
        self.room_group_name = f'theater_{self.theater_id}_seats'

        # Join the WebSocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # Send initial seat availability to the WebSocket
        await self.send_seat_availability()

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # This function could handle messages from the client (if needed)
        pass

    # Send seat availability to WebSocket
    async def send_seat_availability(self):
        # Fetch seat availability for the given theater
        seats = Seat.objects.filter(theater_id=self.theater_id)

        seat_data = []
        for seat in seats:
            seat_data.append({
                'seat_number': seat.seat_number,
                'is_booked': seat.is_booked,
            })

        # Send seat data to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'seat_availability',
            'seats': seat_data,
        }))

    # Function to broadcast seat availability updates
    async def broadcast_seat_update(self, seat_number, is_booked):
        await self.send(text_data=json.dumps({
            'type': 'seat_update',
            'seat_number': seat_number,
            'is_booked': is_booked,
        }))
