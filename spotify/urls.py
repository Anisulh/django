from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path("auth-url", views.AuthUrl, name="auth_url"),
    path("redirect", views.spotifyCallback, name="redirect"),
    path("authenticate", views.IsAuthenticated, name="authenticate"),
    path("pause", views.PauseSong),
    path("play", views.resumeSong),
    path("next", views.NextSong),
    path("prev", views.PrevSong),
    path("search", views.Search),
    path("set-track", views.setTrack),
    path("transfer", views.transferPlay),
]

urlpatterns = format_suffix_patterns(urlpatterns)
