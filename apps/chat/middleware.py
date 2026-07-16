from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import get_user_model

User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class JwtAuthMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):

        scope["user"] = AnonymousUser()

        try:
            query_string = scope["query_string"].decode()

            params = parse_qs(query_string)

            token = params.get("token")

            if token:
                token = token[0]

                access_token = AccessToken(token)

                user_id = access_token["user_id"]

                user = await get_user(user_id)

                scope["user"] = user

        except (TokenError, KeyError, UnicodeDecodeError):
            pass

        return await self.app(scope, receive, send)