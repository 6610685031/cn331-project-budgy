import json
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Transaction, Account, Category, MonthReport, Income, Expense


# Create your views here
@login_required(login_url="/login/")
def landing_page(request, user_id=None):
    if request.path == "/":
        return redirect("/" + str(request.user.id) + "/home/")
    return redirect("/" + str(request.user.id) + request.path)


@login_required(login_url="/login/")
def home_page(request, user_id):
    return render(request, "home/home.html")


@login_required(login_url="/login/")
def dashboard_today_page(request, user_id):

    return render(request, "home/dashboard.html")


@login_required(login_url="/login/")
def back_month_dashboard(request, user_id):

    return render(request, "home/dashboard.html")


@login_required(login_url="/login/")
@csrf_exempt
def category_list(request, user_id):
    user = request.user

    if request.method == "POST":
        # Add Category
        category_name = request.POST.get("category_name")
        if category_name:
            # Avoid duplicate categories
            Category.objects.get_or_create(
                user=user,
                category_name=category_name,
                defaults={"trans_type": "Expense"},
            )

        # Delete Category
        delete_name = request.POST.get("delete_category_name")
        if delete_name:
            Category.objects.filter(user=user, category_name=delete_name).delete()

        return redirect(
            request.META.get("HTTP_REFERER") or "category_list", user_id=request.user.id
        )  # Redirect to the same page to refresh the list

    else:
        # GET Request: Fetch all categories for the user
        categories = Category.objects.filter(user=user)
        return render(request, "home/category_list.html", {"categories": categories})


@login_required(login_url="/login/")
@csrf_exempt
def transaction_income_page(request, user_id):
    user_now = request.user
    transaction_type = "income"

    if request.method == "POST":
        if "date" not in request.POST:
            category_list(request, user_id)
        else:

            date = request.POST["date"]
            amount = request.POST["amount"]
            name_category = request.POST["category"]
            account_name = request.POST["account"]

            # fetch category from database by user, category_name and type
            category_check = Category.objects.filter(
                user=user_now, category_name=name_category, trans_type=transaction_type
            )

            account = Account.objects.get(account_name=account_name)

            # Check if this category exist
            if not category_check.exists():
                category = Category.objects.create(
                    user=user_now,
                    category_name=name_category,
                    trans_type=transaction_type,
                )
            else:
                category = category_check.first()

            # create transaction income model
            income = Income.objects.create(
                user=user_now,
                trans_type=transaction_type,
                date=date,
                amount=amount,
                category=category,
                to_account=account,
            )

            return redirect(reverse("transaction_income"))

    context = {
        "today": timezone.now().date(),
        "categories": Category.objects.filter(user=request.user),
    }
    return render(request, "home/transaction.html", context)


@login_required(login_url="/login/")
def transaction_expense_page(request, user_id):
    return render(request, "home/transaction.html")


@login_required(login_url="/login/")
def transaction_transfer_page(request, user_id):
    return render(request, "home/transaction.html")


@login_required(login_url="/login/")
def stats_page(request, user_id):
    return render(request, "home/stats.html")


@login_required(login_url="/login/")
def settings_page(request, user_id):
    return render(request, "home/settings.html")
