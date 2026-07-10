"""
URL configuration for social_network project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.accounts.views import *
from apps.follows.views import *
from apps.posts.views import *
from apps.notifications.views import *
from apps.stories.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
#accounts
    path('api/register/', RegisterView.as_view()),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/profile/<str:username>/', ProfileView.as_view()),
#follows
    path('api/follow/<str:username>/', FollowView.as_view()),
    path('api/follower/', FollowerListView.as_view()),
    path('api/following/', FollowingListView.as_view()),
#likes
    path('api/post/<int:post_id>/like/', LikeView.as_view()),
#comments
    path('api/post/<int:post_id>/comment/', CommentListCreateView.as_view()),
    path('api/comment/<int:pk>/',CommentDetailView.as_view()),
#feed
    path('api/feed/',FeedView.as_view()),
#save post
    path('api/post/<int:post_id>/save/',SavePostView.as_view()),
    path('api/post/saved/',SavePostListView.as_view()),
#search user
    path('api/search/users/',UserSearchView.as_view()),
    path('api/search/posts/',PostSearchView.as_view()),
#notifications
    path('api/notifications/',NotificationListView.as_view()),
    path('api/notifications/unread-count/',UnreadNotificationView.as_view()),
    path('api/notifications/<int:id>/read/',ReadNotificationView.as_view()),
    path('api/notifications/read-all/',ReadAllNotificationView.as_view()),
#stories
    path('api/stories/',StoryCreateView.as_view()),
    path('api/stories/<int:pk>/',StoryDeleteView.as_view()),
    path('api/stories/user/<str:username>/',UserStoryListView.as_view()),
    path('api/stories/feed/',StoryFeedView.as_view()),
    path('api/stories/<int:story_id>/view/',StoryViewCreateView.as_view()),
    path('api/stories/<int:story_id>/viewers/',StoryViewerListView.as_view()),

]

#posts
router = DefaultRouter()
router.register(r'api/post', PostViewset, basename="post")
urlpatterns += router.urls