from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .serializers import RegisterSerializer
from .models import Profile
from .serializers import ProfileSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class ProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer

    def get_object(self):
        obj = get_object_or_404(
            Profile,
            user__username=self.kwargs["username"]
        )

        self.check_object_permissions(self.request, obj)

        return obj