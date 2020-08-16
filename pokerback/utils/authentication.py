import typing
import uuid

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from pokerback.user.models import User


class Player(typing.NamedTuple):
    uuid: str
    is_authenticated: bool = True


class PlayerAuthentication(BaseAuthentication):
    def get_user(self, request):
        if "uuid" not in request.session:
            request.session["uuid"] = str(uuid.uuid4())
        return Player(uuid=request.session["uuid"])

    def authenticate(self, request):
        return self.get_user(request), None


class HostAuthentication(BaseAuthentication):
    def get_user(self):
        user, created = User.objects.get_or_create(defaults={"uuid": uuid.uuid4()},)
        return user

    def authenticate(self, request):
        return self.get_user(), None
