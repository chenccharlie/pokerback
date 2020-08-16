from django.conf.urls import url

from pokerback.room import player_views


urlpatterns = [
    url(r"^$", player_views.RetrieveRoomView.as_view(), name="player_room-retrieve",),
]
