from django.urls import path
from .views import RobotsList, RobotDetail, RobotsSummary

urlpatterns = [
    path('api/robots', RobotsList.as_view()),
    path('api/robots/<int:id>', RobotDetail.as_view()),
    path('api/robots_report', RobotsSummary.as_view())
]