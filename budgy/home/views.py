import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
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
def category_add(request, user_id):
    user = request.user

    if request.method == "POST":
        name = request.POST["category_name"]
        type = request.POST["trans_type"]

        category = Category.objects.create(
            user=user, category_name=name, trans_type=type
        )
        category.save()
        return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def category_delete(request, user_id):
    user = request.user

    if request.method == "POST":
        name = request.POST["category_name"]
        type = request.POST["trans_type"]

        category = get_object_or_404(
            Category, category_name=name, user=user, trans_type=type
        )
        category.delete()
        return JsonResponse({"success": True}, status=200)


@login_required(login_url="/login/")
def transaction_income_page(request, user_id):
    user = request.user
    transaction_type = "income"

    if request.method == "POST":
        date = request.POST["date"]
        amount = request.POST["amount"]
        category_name = request.POST["category_name"]
        account_name = request.POST["account"]

        # fetch category from database by user, category_name and type
        category_check = Category.objects.filter(
            user=user, category_name=category_name, trans_type=transaction_type
        )

        account = Account.objects.get(account_name=account_name, user=user)

        # Check if this category exist
        if not category_check.exists():
            category = Category.objects.create(
                user=user, category_name=category_name, trans_type=transaction_type
            )
        else:
            category = category_check.first()

        # create transaction income model
        income = Income.objects.create(
            user=user,
            trans_type=transaction_type,
            date=date,
            amount=amount,
            category=category,
            to_account=account,
        )

        return redirect("transaction_income")

    category_list = Category.objects.all()

    context = {"today": timezone.now().date(), "category_list": category_list}
    return render(request, "home/transaction_income.html", context)


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
