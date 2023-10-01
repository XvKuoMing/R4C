from django.urls import path
from .views import CustomerLogIn, CustomerLogOut

urlpatterns = [
    path('login', CustomerLogIn.as_view()),
    path('logout', CustomerLogOut.as_view())
]