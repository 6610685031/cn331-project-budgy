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


@csrf_exempt
def category_list(request):
    user = request.user
    if request.method == "GET":
        categories = Category.objects.filter(user=user).values(
            "category_name", "trans_type"
        )
        return JsonResponse(list(categories), safe=False)

    elif request.method == "POST":
        data = json.loads(request.body)
        name = data.get("category_name")
        trans_type = data.get("trans_type", "Expense")
        if not name:
            return JsonResponse({"error": "category_name required"}, status=400)

        cat, created = Category.objects.get_or_create(
            user=user, category_name=name, defaults={"trans_type": trans_type}
        )
        return JsonResponse({"created": created, "category": name})

    elif request.method == "DELETE":
        data = json.loads(request.body)
        name = data.get("category_name")
        Category.objects.filter(user=user, category_name=name).delete()
        return JsonResponse({"deleted": name})


@login_required(login_url="/login/")
def transaction_income_page(request):
    user_now = request.user
    transaction_type = "income"

    if request.method == "POST":
        date = request.POST["date"]
        amount = request.POST["amount"]
        name_category = request.POST["category_name"]
        account_name = request.POST["account"]

        # fetch category from database by user, category_name and type
        category_check = Category.objects.filter(
            user=user_now, category_name=name_category, trans_type=transaction_type
        )

        # Check if this category exist
        if not category_check.exists():
            category = Category.objects.create(
                user=user_now, category_name=name_category, trans_type=transaction_type
            )
        else:
            category = category_check.first()

        # create transaction income model
        income = Income.objects.create(
            user=user_now,
            trans_type=transaction_type,  # หรือ "expense" ขึ้นอยู่กับประเภท
            date=date,
            amount=amount,
            category=category,
            to_account=account,
        )

        return redirect(reverse("transaction_income"))

    context = {
        "today": timezone.now().date(),
    }
    return render(request, "home/transaction.html", context)


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
