from django.shortcuts import render
from .services import (
    follow_user,
    unfollow_user,
    get_followers, 
    get_followings
)
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Follow
from .serializers import FollowerListSerializer, FollowingListSerializer
from apps.notifications.services import NotificationService
from django.contrib.auth import get_user_model

User = get_user_model()


class FollowView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, username):
        result = follow_user(request.user, username)

        NotificationService.create_follow_notification(
            recipient=User.objects.get(username=username),
            actor=request.user,
        )

        return Response({'status': result}, status=status.HTTP_201_CREATED)
    
    def delete(self, request, username):
        result = unfollow_user(request.user, username)
        return Response({'status': result}, status=status.HTTP_204_NO_CONTENT)


class FollowerListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = FollowerListSerializer(
            get_followers(request.user),
            many=True
        )
        return Response(serializer.data)


class FollowingListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = FollowingListSerializer(
            get_followings(request.user),
            many=True
        )
        return Response(serializer.data)


