from django.urls import path
from . import views

urlpatterns = [
    path("<str:username>/home/", views.home_page, name="home_page"),
]
