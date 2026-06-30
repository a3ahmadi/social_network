from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.views import APIView
from .serializers import RegisterSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
