from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.


# To User Home Page
def home(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login")
        return redirect(reverse("login"))

    return render(request, "home/home.html")


# Login function
def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            # admin:index เป็น url ที่ Django กำหนดไว้ให้เป็นหน้า admin page
            # return redirect(reverse("admin:index"))

            return redirect(reverse("home"))  # return render(request, "room/home.html")

        else:
            messages.error(request, "This user is not registry yet")
            return redirect(reverse("login"))

    return render(request, "authorized/login.html")


# Logout function
def logout(request):
    logout(request)
    context = {"message": "You're Logout"}
    return render(request, "authorized/login.html", context)


# Register function
def register(request):
    if request.method == "POST":
        username = request.POST["Username"]
        password = request.POST["Password"]
        email = request.POST["email"]
        password_again = request.POST["confirm_password"]

        if password != password_again:
            return render(
                request,
                "authorized/register.html",
                {"message": "Password not match, Please try again."},
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "authorized/register.html",
                {"message": "This Username already registry, Please try again."},
            )

        User.objects.create_user(username=username, password=password, email=email)
        return render(
            request,
            "authorized/login.html",
            {"registry": "Register success"},
        )
    return render(request, "authorized/register.html")
