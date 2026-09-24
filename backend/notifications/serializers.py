from rest_framework import serializers

from .models import Notification, DeviceToken


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['id', 'token', 'platform', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'title', 'message',
            'notification_type', 'related_object_type', 'related_object_id',
            'is_read', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
