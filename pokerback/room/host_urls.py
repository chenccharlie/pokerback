from django.conf.urls import url

from pokerback.room import host_views


urlpatterns = [
    url(r"^create/$", host_views.CreateRoomView.as_view(), name="host_room-create",),
    url(r"^$", host_views.RetrieveRoomView.as_view(), name="host_room-retrieve",),
]
