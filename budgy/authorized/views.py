from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.


# Login function
def login(request):
    if request.user.is_authenticated:
        # User is logged in, redirect to previous page or home
        return redirect(
            request.META.get("HTTP_REFERER") or "home", user_id=request.user.id
        )

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)
            # admin:index เป็น url ที่ Django กำหนดไว้ให้เป็นหน้า admin page
            # return redirect(reverse("admin:index"))

            return redirect(
                "home", user_id=request.user.id
            )  # return render(request, "room/home.html")

        else:
            messages.error(request, "This user is not registry yet")
            return redirect("login")

    return render(request, "authorized/login.html")


# Logout function
def logout(request):
    auth_logout(request)
    context = {"message": "You're Logout"}
    return redirect(reverse("login"), context)


# Register function
def register(request):
    if request.user.is_authenticated:
        # User is logged in, redirect to previous page or home
        return redirect(
            request.META.get("HTTP_REFERER") or "home", user_id=request.user.id
        )

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
