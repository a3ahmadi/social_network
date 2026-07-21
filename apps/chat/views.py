from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from .permissions import IsOwner
from django.shortcuts import get_object_or_404
from apps.chat.models import Conversation, Message
from .serializers import *
from core.pagination import LimitOffsetPaginations

User = get_user_model()


class conversationsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationListSerializer
    pagination_class = LimitOffsetPaginations

    def get_queryset(self):
        return Conversation.objects.filter(
            users=self.request.user
        )
    

class ConversationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.data.get("username")

        if not username:
            return Response(
                {"detail": "username is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        other_user = get_object_or_404(
            User,
            username=username
        )

        if other_user == request.user:
            return Response(
                {"detail": "You cannot chat with yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = (
            Conversation.objects
            .filter(users=request.user)
            .filter(users=other_user)
            .first()
        )

        if conversation:
            return Response({
                "id": conversation.id,
                "created": False
            })

        conversation = Conversation.objects.create()
        conversation.users.add(
            request.user,
            other_user
        )

        return Response({
            "id": conversation.id,
            "created": True
        }, status=status.HTTP_201_CREATED)
    

class ConversationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationDetailSerializer

    def get_queryset(self):
        return Conversation.objects.filter(
            users=self.request.user
        ).prefetch_related("users")
    

class ConversationMessageListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationMessageSerializer
    pagination_class = LimitOffsetPaginations

    def get_queryset(self):
        conversation = get_object_or_404(
            Conversation.objects.filter(
                users=self.request.user
            ),
            id=self.kwargs["id"]
        )

        return Message.objects.filter(
            conversation=conversation
        ).select_related("sender")


class MessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        conversation = get_object_or_404(
            Conversation.objects.filter(
                users=request.user
            ),
            id=id
        )

        text = request.data.get("text")

        if not text:
            return Response(
                {"detail": "text is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            text=text
        )

        serializer = ConversationMessageSerializer(message)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    

class MessageDestroyView(generics.DestroyAPIView):
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


class MessageUpdateView(generics.UpdateAPIView):
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ConversationMessageSerializer


class ReadingMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        conversation = get_object_or_404(
            Conversation.objects.filter(
                users=request.user
            ),
            id=id
        )

        updated_count = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(
            sender=request.user
        ).update(
            is_read=True
        )

        return Response({"messages_read": updated_count})
    

class UnreadCountMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread = Message.objects.filter(
            conversation__users=request.user,
            is_read=False
        ).exclude(
            sender=request.user
        ).distinct().count()

        return Response({"count": unread})
    

class SearchConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get("q")

        if not q:
            return Response(
                {"detail": "q is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversations = Conversation.objects.filter(
            users=request.user
        ).prefetch_related("users", "messages")

        conversations = [
            conversation
            for conversation in conversations
            if conversation.users.exclude(
                id=request.user.id
            ).filter(
                username__icontains=q
            ).exists()
        ]

        serializer = ConversationSearchSerializer(
            conversations,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)
