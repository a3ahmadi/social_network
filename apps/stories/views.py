from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from .models import Story, StoryView
from apps.follows.models import Follow
from apps.posts.permissions import IsOwner
from django.utils import timezone
from django.db.models import Q
from django.db.models import Prefetch

User = get_user_model()

class StoryCreateView(generics.CreateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            user = self.request.user
        )


class StoryDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Story.objects.all()


class UserStoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StorySerializer

    def get_queryset(self):
        return Story.objects.filter(
            user__username=self.kwargs["username"],
            expires_at__gt=timezone.now()
        )
    

class StoryFeedView(generics.ListAPIView):
    serializer_class = StoryFeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        following_ids = Follow.objects.filter(
            follower=self.request.user
        ).values_list(
            "following_id",
            flat=True
        )

        return User.objects.filter(
            Q(id=self.request.user.id) |
            Q(id__in=following_ids),
            stories__expires_at__gt=timezone.now()
        ).prefetch_related(
            Prefetch(
                "stories",
                queryset=Story.objects.filter(
                    expires_at__gt=timezone.now()
                )
            )
        ).distinct()


class StoryViewCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, story_id):
        _, created = StoryView.objects.get_or_create(
            user=request.user,
            story_id=story_id
        )

        if created:
            return Response({"message": "created"})
        
        return Response({"message": "Seen_before"})


class StoryViewerListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = StoryUserSerializer

    def get_queryset(self):
        viewers_id = StoryView.objects.filter(
            story_id=self.kwargs["story_id"],
            user=self.request.user
        ).values_list(
            "user_id",
            flat=True
        )
        return User.objects.filter(
            id__in=viewers_id,
        )
    

