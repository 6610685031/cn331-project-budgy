from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Transaction, Account, Category, MonthReport, Income, Expense


# Create your views here
@login_required(login_url="/login/")
# def home_page(request, username):
def home_page(request):
    # return render(request, "home/home.html", {"user": user})
    return render(request, "home/home.html")


@login_required(login_url="/login/")
def dashboard_today_page(request):

    return render(request, "home/dashboard.html")


@login_required(login_url="/login/")
def back_month_dashboard(request):

    return render(request, "home/dashboard.html")


@login_required(login_url="/login/")
def transaction_income_page(request):

    return render(request, "home/transaction.html")


@login_required(login_url="/login/")
def transaction_expense_page(request):
    return render(request, "home/transaction.html")


@login_required(login_url="/login/")
def transaction_transfer_page(request):
    return render(request, "home/transaction.html")


@login_required(login_url="/login/")
def stats_page(request):
    return render(request, "home/stats.html")


@login_required(login_url="/login/")
def settings_page(request):
    return render(request, "home/settings.html")
