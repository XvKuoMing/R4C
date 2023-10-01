from django.urls import path
from .views import get_robots


urlpatterns = [
    path('api/robots/<str:serial>', get_robots)
]