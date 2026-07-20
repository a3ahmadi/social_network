from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync

from .models import Notification


class NotificationService:

    @staticmethod
    def create_notification(
        *,
        recipient,
        actor,
        notification_type,
        post=None,
        comment=None,
    ):

        if recipient == actor:
            return None
        
        if notification_type == Notification.NotificationType.FOLLOW:

            exists = Notification.objects.filter(
                recipient=recipient,
                actor=actor,
                notification_type=notification_type,
            ).exists()

            if exists:
                return None
            
        elif notification_type == Notification.NotificationType.POST_LIKE:

            exists = Notification.objects.filter(
                recipient=recipient,
                actor=actor,
                notification_type=notification_type,
                post=post,
            ).exists()

            if exists:
                return None

        notification = Notification.objects.create(
            recipient=recipient,
            actor=actor,
            notification_type=notification_type,
            post=post,
            comment=comment,
        )

        channel_layer = get_channel_layer()

        async_to_sync(
            channel_layer.group_send
        )(
            f"notifications_{recipient.id}",
            {
                "type": "send_notification",
                "data": {
                    "id": notification.id,
                    "actor": actor.username,
                    "notification_type": notification.notification_type,
                    "post_id": post.id if post else None,
                    "comment_id": comment.id if comment else None,
                    "is_read": False,
                    "created_at": (
                        notification.created_at.isoformat()
                    ),
                }
            }
        )

        return notification
    
    @staticmethod
    def create_follow_notification(
        *,
        recipient,
        actor,
    ):

        return NotificationService.create_notification(
            recipient=recipient,
            actor=actor,
            notification_type=(
                Notification.NotificationType.FOLLOW
            ),
        )
    
    @staticmethod
    def create_post_like_notification(
        *,
        recipient,
        actor,
        post,
    ):

        return NotificationService.create_notification(
            recipient=recipient,
            actor=actor,
            notification_type=(
                Notification.NotificationType.POST_LIKE
            ),
            post=post,
        )
    
    @staticmethod
    def create_post_comment_notification(
        *,
        recipient,
        actor,
        post,
        comment,
    ):

        return NotificationService.create_notification(
            recipient=recipient,
            actor=actor,
            notification_type=(
                Notification.NotificationType.POST_COMMENT
            ),
            post=post,
            comment=comment,
        )
    
    @staticmethod
    def create_comment_reply_notification(
        *,
        recipient,
        actor,
        post,
        comment,
    ):

        return NotificationService.create_notification(
            recipient=recipient,
            actor=actor,
            notification_type=(
                Notification.NotificationType.COMMENT_REPLY
            ),
            post=post,
            comment=comment,
        )
    
    