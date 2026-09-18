from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Room, RoomMapPosition
User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'date_joined', 
            'is_active'
        ]
        read_only_fields = ['id', 'date_joined']

class RoomMapPositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoomMapPosition
        fields = [
            "x",
            "y",
            "width",
            "height",
            "is_visible",
        ]


class RoomSerializer(serializers.ModelSerializer):

    map_position = RoomMapPositionSerializer(
        read_only=True
    )

    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "room_type",
            "price",
            "map_position",
        ]