from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Post, Comment, SavedPost
from apps.follows.models import Follow
from apps.accounts.models import Profile
from rest_framework import status
from rest_framework.response import Response
from .permissions import IsOwner
from django.db.models import Q
from apps.notifications.services import NotificationService
from django.shortcuts import get_object_or_404
from core.pagination import CursorPaginations, LimitOffsetPaginations
from django.db.models import F
from .serializers import (
    PostSerializer,
    LikeListSerializer,
    CommentListSerializer,
    CommentUpdateSerializer,
    CommentDetailSerializer,
    CommentCreateSerializer,
    UserListSerializer
)
from .services import(
    like_post,
    unlike_post,
    post_likes_list,
    save_post,
    delete_saved_post
)

User = get_user_model()


class PostViewset(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPaginations

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        Profile.objects.filter(
            user=self.request.user
        ).update(
            posts_count=F('posts_count') + 1
        )

    def perform_destroy(self, instance):
        Profile.objects.filter(
            user=self.request.user
        ).update(
            posts_count=F('posts_count') - 1
        )

        instance.delete()


class LikeView(APIView):
    def get(self, request, post_id):
        likes = post_likes_list(post_id)

        paginator = LimitOffsetPaginations()
        page = paginator.paginate_queryset(
            likes,
            request,
            view=self
        )

        serializer = LikeListSerializer(page, many=True)

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request, post_id):
        result = like_post(request.user, post_id)
        
        post = get_object_or_404(Post, id=post_id)

        NotificationService.create_post_like_notification(
            actor=request.user,
            recipient=post.user,
            post=post
        )

        return Response({'status': result}, status=status.HTTP_201_CREATED)
    
    def delete(self, request, post_id):
        result = unlike_post(request.user, post_id)
        return Response({'status': result}, status=status.HTTP_204_NO_CONTENT)
    

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPaginations

    def get_queryset(self):
        return Comment.objects.filter(
        post_id=self.kwargs["post_id"],
        parent=None
    )

    def perform_create(self, serializer):
        comment = serializer.save(
            user=self.request.user,
            post_id=self.kwargs["post_id"]
        )

        post = get_object_or_404(
                Post,
                id=self.kwargs["post_id"]
            )

        if comment.parent is None:

            NotificationService.create_post_comment_notification(
                recipient=post.user,
                actor=self.request.user,
                post=post,
                comment=comment,
            )

        else:
            
            NotificationService.create_comment_reply_notification(
                    recipient=post.user,
                    actor=self.request.user,
                    post=post,
                    comment=comment,
                )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer

        return CommentListSerializer


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return CommentUpdateSerializer

        return CommentDetailSerializer


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CursorPaginations

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
    

class SavePostView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, post_id):
        result = save_post(post_id, request.user)
        return Response({'status': result}, status=status.HTTP_201_CREATED)
    
    def delete(self, request, post_id):
        result = delete_saved_post(post_id, request.user)
        return Response({'status': result}, status=status.HTTP_204_NO_CONTENT)


class SavePostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPaginations

    def get_queryset(self):
        return Post.objects.filter(
            saved_by__user=self.request.user
        )
    

class UserSearchView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPaginations

    def get_queryset(self):
        query = self.request.query_params.get("q", "")
        return Profile.objects.filter(
            Q(name__icontains=query) |
            Q(user__username__icontains=query)
        )
    

class PostSearchView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPaginations

    def get_queryset(self):
        query = self.request.query_params.get("q", "")
        return Post.objects.filter(
            Q(caption__icontains=query) |
            Q(location__icontains=query)
        )