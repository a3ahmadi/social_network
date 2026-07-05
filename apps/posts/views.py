from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Post
from rest_framework import status
from rest_framework.response import Response
from .serializers import PostSerializer, LikeListSerializer
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
    

