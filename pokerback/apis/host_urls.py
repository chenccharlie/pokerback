from django.conf.urls import url

from pokerback.apis import host_views


urlpatterns = [
    url(r"^create/$", host_views.CreateRoomView.as_view(), name="host_room-create",),
    url(
        r"^close/$", host_views.CloseRoomView.as_view(), name="host_room-update-close",
    ),
    url(
        r"^start_game/$",
        host_views.StartGameView.as_view(),
        name="host_game-update-start",
    ),
    url(r"^view/$", host_views.RetrieveRoomView.as_view(), name="host_room-retrieve",),
]
