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

    if request.method == "POST":
        date = request.POST["date"]
        amount = request.POST["amount"]
        category = request.POST["category"]
        account = request.POST["account"]
        note = request.POST["note"]

        transaction = Transaction.objects.create(
            user=user,
            trans_type="income",  # หรือ "expense" ขึ้นอยู่กับประเภท
            date=timezone.now(),
            amount=1500.0,
            category=category,
        )

        return redirect("transaction_list")

    context = {
        "today": timezone.now().date(),
    }
    return render(request, "home/transaction.html", context)


def transaction_expense_page(request):
    return render(request, "home/transaction.html")


def transaction_transfer_page(request):
    return render(request, "home/transaction.html")


def stats_page(request):
    return render(request, "home/stats.html")


def settings_page(request):
    return render(request, "home/settings.html")
