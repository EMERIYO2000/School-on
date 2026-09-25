from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import DeviceToken, Notification
from .serializers import DeviceTokenSerializer, NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = get_object_or_404(self.get_queryset(), pk=pk)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification, context={'request': request}).data)


class DeviceTokenViewSet(viewsets.GenericViewSet):
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='me')
    def set_device_token(self, request):
        token = request.data.get('token')
        platform = request.data.get('platform', 'android')

        if not token:
            return Response({'error': 'Le token est requis.'}, status=status.HTTP_400_BAD_REQUEST)

        obj, _ = DeviceToken.objects.update_or_create(
            user=request.user,
            defaults={'token': token, 'platform': platform},
        )
        return Response(DeviceTokenSerializer(obj).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='me')
    def delete_device_token(self, request):
        DeviceToken.objects.filter(user=request.user).delete()
        return Response({'message': 'Token appareil supprimé.'}, status=status.HTTP_200_OK)
