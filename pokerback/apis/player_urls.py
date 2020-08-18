from django.conf.urls import url

from pokerback.apis import player_views


urlpatterns = [
    url(
        r"^view/$",
        player_views.RetrieveRoomView.as_view(),
        name="player_room-retrieve",
    ),
    url(r"^signin/$", player_views.SigninView.as_view(), name="player-update-signin",),
    url(r"^sit/$", player_views.SitRoomView.as_view(), name="player_room-update-sit",),
]
