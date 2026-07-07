from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Post, Comment
from apps.follows.models import Follow
from rest_framework import status
from rest_framework.response import Response
from .permissions import IsCommentOwner
from django.db.models import Q
from .serializers import (
    PostSerializer,
    LikeListSerializer,
    CommentListSerializer,
    CommentUpdateSerializer,
    CommentDetailSerializer,
    CommentCreateSerializer,
    Feedserializer
)
from .services import(
    like_post,
    unlike_post,
    post_likes_list
)


class PostViewset(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeView(APIView):
    def get(self, request, post_id):
        result = post_likes_list(post_id)
        serializer = LikeListSerializer(result, many=True)
        return Response(serializer.data)

    def post(self, request, post_id):
        result = like_post(request.user, post_id)
        return Response({'status': result}, status=status.HTTP_201_CREATED)
    
    def delete(self, request, post_id):
        result = unlike_post(request.user, post_id)
        return Response({'status': result}, status=status.HTTP_204_NO_CONTENT)
    

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(
        post_id=self.kwargs["post_id"],
        parent=None
    )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            post_id=self.kwargs["post_id"]
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer

        return CommentListSerializer


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated, IsCommentOwner]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return CommentUpdateSerializer

        return CommentDetailSerializer


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        following_ids = Follow.objects.filter(
            follower=self.request.user
        ).values_list(
            "following_id",
            flat=True
        )

        return Post.objects.filter(
            Q(user=self.request.user) |
            Q(user_id__in=following_ids)
        ).select_related(
            "user",
            "user__profile"
        ).order_by(
            "-created_at"
        )

