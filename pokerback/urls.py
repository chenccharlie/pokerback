from django.conf.urls import url
from django.urls import include


urlpatterns = [
    # Player URLs
    url(r"^room/", include("pokerback.room.player_urls")),
    # Host URLs
    url(r"^host/room/", include("pokerback.room.host_urls")),
]
