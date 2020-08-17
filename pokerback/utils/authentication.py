import typing
import uuid

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from pokerback.user.models import User


class PlayerSigninAuthed(typing.NamedTuple):
    is_authenticated: bool = True


class PlayerSigninAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return PlayerSigninAuthed(), None


class Player(typing.NamedTuple):
    uuid: str
    name: str
    room_key: str
    is_authenticated: bool = True


class PlayerAuthentication(BaseAuthentication):
    def get_user(self, request):
        try:
            return Player(
                uuid=request.session["uuid"],
                name=request.session["name"],
                room_key=request.session["room_key"],
            )
        except Exception as e:
            raise AuthenticationFailed()

    def authenticate(self, request):
        return self.get_user(request), None


class HostAuthentication(BaseAuthentication):
    def get_user(self):
        user, created = User.objects.get_or_create(defaults={"uuid": uuid.uuid4()},)
        return user

    def authenticate(self, request):
        return self.get_user(), None
