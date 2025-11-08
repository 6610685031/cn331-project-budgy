import json
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
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


@login_required
def spending_api(request):
    mode = request.GET.get("mode")
    user = request.user
    spendings = Transaction.objects.filter(user=user)

    if mode == "daily":
        date_str = request.GET.get("date")
        if date_str:
            selected_date = parse_date(date_str)
            spendings = spendings.filter(date__date=selected_date)
    elif mode == "monthly":
        month_str = request.GET.get("month")  # YYYY-MM
        if month_str:
            year, month = map(int, month_str.split("-"))
            spendings = spendings.filter(date__year=year, date__month=month)
    elif mode == "yearly":
        year_str = request.GET.get("year")
        if year_str:
            spendings = spendings.filter(date__year=int(year_str))

    # แปลงเป็น list JSON
    data = [
        {
            "category": t.category.category_name if t.category else "Uncategorized",
            "amount": t.amount,
            "type": t.trans_type,
        }
        for t in spendings.order_by("-date")  # เรียงจากล่าสุด
    ]

    return JsonResponse({"spendings": data})


@login_required
def accounts_api(request):
    user = request.user
    accounts = Account.objects.filter(user=user).order_by("-id")[:3]

    data = [
        {
            "name": acc.account_name,
            "balance": acc.balance,
        }
        for acc in accounts
    ]

    total_balance = sum(acc.balance for acc in Account.objects.filter(user=user))

    return JsonResponse({"accounts": data, "total_balance": total_balance})


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
                defaults={"trans_type": "income"},
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
        return render(
            request,
            "home/category_list.html",
            {"categories": categories},
        )


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
            name_category = request.POST["category_name"]
            account_name = request.POST["account"]

            # fetch category from database by user, category_name and type
            category_check = Category.objects.filter(
                user=user_now, category_name=name_category, trans_type=transaction_type
            )

            account = Account.objects.get(user=user_now, account_name=account_name)

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

            account.balance += float(amount)
            account.save()

            return redirect(
                reverse("transaction_income", kwargs={"user_id": request.user.id})
            )

    context = {
        "categories": Category.objects.filter(
            user=request.user, trans_type=transaction_type
        ),
    }
    return render(request, "home/transaction_income.html", context)


@login_required(login_url="/login/")
@csrf_exempt
def transaction_expense_page(request, user_id):
    user_now = request.user
    transaction_type = "expense"

    if request.method == "POST":
        if "date" not in request.POST:
            category_list(request, user_id)
        else:

            date = request.POST["date"]
            amount = request.POST["amount"]
            name_category = request.POST["category_name"]
            account_name = request.POST["account"]

            # fetch category from database by user, category_name and type
            category_check = Category.objects.filter(
                user=user_now, category_name=name_category, trans_type=transaction_type
            )

            account = Account.objects.get(user=user_now, account_name=account_name)

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
            expense = Expense.objects.create(
                user=user_now,
                trans_type=transaction_type,
                date=date,
                amount=amount,
                category=category,
                from_account=account,
            )

            account.balance -= float(amount)
            account.save()

            return redirect(
                reverse("transaction_expense", kwargs={"user_id": request.user.id})
            )

    context = {
        "categories": Category.objects.filter(
            user=request.user, trans_type=transaction_type
        ),
    }
    return render(request, "home/transaction_expense.html")


@login_required(login_url="/login/")
@csrf_exempt
def transaction_transfer_page(request, user_id):
    user_now = request.user
    transaction_type = "transfer"

    if request.method == "POST":
        if "date" not in request.POST:
            category_list(request, user_id)
        else:

            date = request.POST["date"]
            amount = request.POST["amount"]
            name_category = request.POST["category_name"]
            from_account = request.POST["from_account"]
            to_account = request.POST["to_account"]

            # fetch category from database by user, category_name and type
            category_check = Category.objects.filter(
                user=user_now, category_name=name_category, trans_type=transaction_type
            )

            from_account = Account.objects.get(user=user_now, account_name=from_account)
            to_account = Account.objects.get(user=user_now, account_name=to_account)

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
            expense = Expense.objects.create(
                user=user_now,
                trans_type=transaction_type,
                date=date,
                amount=amount,
                category=category,
                from_account=from_account,
            )

            income = Income.objects.create(
                user=user_now,
                trans_type=transaction_type,
                date=date,
                amount=amount,
                category=category,
                to_account=to_account,
            )

            from_account.balance -= float(amount)
            from_account.save()

            to_account.balance += float(amount)
            to_account.save()

            return redirect(
                reverse("transaction_transfer", kwargs={"user_id": request.user.id})
            )

    context = {
        "categories": Category.objects.filter(
            user=request.user, trans_type=transaction_type
        ),
    }
    return render(request, "home/transaction_transfer.html")


@login_required(login_url="/login/")
def stats_page(request, user_id):
    return render(request, "home/stats.html")


@login_required(login_url="/login/")
def settings_page(request, user_id):
    return render(request, "home/settings.html")
