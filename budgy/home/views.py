from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime
from django.urls import reverse
from .models import Transaction, Account, Category, MonthReport, Income, Expense


# Create your views here.
def home_page(request, username):
    user = get_object_or_404(User, username=username)

    return render(request, "home/home.html", {"user": user})


def dashboard_today_page(request):

    return render(request, "home/dashboard.html")


def back_month_dashboard(request):

    return render(request, "home/dashboard.html")


def transaction_income_page(request):

    return render(request, "home/transaction.html", context)


def transaction_expense_page(request):
    return render(request, "home/transaction.html")


def transaction_transfer_page(request):
    return render(request, "home/transaction.html")


def stats_page(request):
    return render(request, "home/stats.html")


def settings_page(request):
    return render(request, "home/settings.html")
