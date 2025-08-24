from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Booking, Room

class RoomSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Room
        fields = ["id", "name", "capacity"]

class BookingSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    room_name = serializers.ReadOnlyField(source="room.name")

    class Meta:
        model = Booking
        fields = [
            "id",
            "room", 
            "room_name",
            "start_at",
            "end_at",
            "status",
            "customer_name",
            "created_at",
            "user",
            ]
        read_only_fields = ["status", "created_at", "user"]

        def create(self, validated_data):
            validated_data["status"] = Booking.Status.CONFIRMED
            user = self.context["request"].user
            if user and user.is_authenticated:
                validated_data["user"] = user
            return super().create(validated_data)

class RoomSerializer(serializers.ModelSerializer):
    booking_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Room
        fields = ["id", "name", "capacity", "booking_count"]