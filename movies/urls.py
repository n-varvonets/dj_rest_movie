from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from . import api


urlpatterns = format_suffix_patterns([
    path("movie/", views.MovieViewSet.as_view({'get': 'list'})),
    path("movie/<int:pk>/", views.MovieViewSet.as_view({'get': 'retrieve'})),
    path("review/", views.ReviewCreateViewSet.as_view({'post': 'create'})),  # по  view  указали только сериализатор, но
    # т.к. хотим мы только создавать или выводить список отзыва, то указываем post
    path("rating/", views.AddStarRatingViewSet.as_view({'post': 'create'})),
    path("actors/", views.ActorsViewSet.as_view({'get': 'list'})),
    path("actors/<int:pk>", views.ActorsViewSet.as_view({'get': 'retrieve'})),
])

""" с использованием  generics"""
# urlpatterns = [
#     path("movie/", views.MovieListView.as_view()),
#     path("movie/<int:pk>/", views.MovieDetailView.as_view()),
#     path("review/", views.ReviewCreateView.as_view()),
#     path("rating/", views.AddStarRatingView.as_view()),
#     path("actors/", views.ActorsListView.as_view()),
#     path("actors/<int:pk>", views.ActorsDetailView.as_view()),
# ]
