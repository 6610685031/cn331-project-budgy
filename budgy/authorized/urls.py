from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("home/", views.home, name="home"),
    path("register/", views.register, name="register"),
]
