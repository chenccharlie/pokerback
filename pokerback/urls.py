from django.conf.urls import url
from django.urls import include


urlpatterns = [
    # Player URLs
    url(r"^", include("pokerback.apis.player_urls")),
    # Host URLs
    url(r"^host/", include("pokerback.apis.host_urls")),
]
