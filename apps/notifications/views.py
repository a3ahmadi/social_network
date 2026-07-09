from .serializers import NotificationSerializer
from django.shortcuts import get_object_or_404
from .models import Notification
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.posts.permissions import IsOwner
from rest_framework.permissions import IsAuthenticated

class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
        "actor",
        "actor__profile",
        "post",
        "comment",
        )
    

class UnreadNotificationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return Response({"unread_count": count})
    

class ReadNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        notif = get_object_or_404(
            Notification,
            id=id,
            recipient=request.user
        )
        
        if not notif.is_read:
            notif.is_read = True
            notif.save(update_fields=["is_read"])
        return Response({
            "message": "notification marked as read"
        })
    

class ReadAllNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(
            is_read=True
        )
        return Response({
            "message": "all notifications marked as read"
        })