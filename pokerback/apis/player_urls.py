from django.conf.urls import url

from pokerback.apis import player_views


urlpatterns = [
    url(r"^$", player_views.RetrieveRoomView.as_view(), name="player_room-retrieve",),
    url(
        r"^join/$", player_views.JoinRoomView.as_view(), name="player_room-update-join",
    ),
]
