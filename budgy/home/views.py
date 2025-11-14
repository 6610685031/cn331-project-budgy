# import json
# import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Transaction, Account, Category, MonthReport, Income, Expense
import calendar



# Create your views here
@login_required(login_url="/login/")
def landing_page(request, user_id=None):
    if request.path == "/":
        return redirect("/" + str(request.user.id) + "/home/")
    return redirect("/" + str(request.user.id) + request.path)


@login_required(login_url="/login/")
def home_page(request, user_id):
    user = request.user
    
    # --- 1. คำนวณยอดเงินคงเหลือทั้งหมด ---
    # ดึงข้อมูล accounts ทั้งหมดของผู้ใช้ แล้วรวมยอด balance
    # หากไม่มี account เลย ให้ค่าเป็น 0
    total_balance = Account.objects.filter(user=user).aggregate(Sum('balance'))['balance__sum'] or 0

    # --- 2. คำนวณยอดรวมของเดือนปัจจุบัน ---
    current_year = datetime.now().year
    current_month = datetime.now().month

    # ยอดรวมรายรับของเดือนปัจจุบัน
    month_income = Income.objects.filter(
        user=user,
        date__year=current_year,
        date__month=current_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # ยอดรวมรายจ่ายของเดือนปัจจุบัน
    month_expense = Expense.objects.filter(
        user=user,
        date__year=current_year,
        date__month=current_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # --- 3. คำนวณสัดส่วนรายจ่ายต่อรายรับ ---
    # ป้องกันการหารด้วยศูนย์ หากเดือนนี้ยังไม่มีรายรับ
    if month_income > 0:
        expense_percentage = (month_expense / month_income) * 100
    else:
        expense_percentage = 0 # ถ้าไม่มีรายรับ ให้สัดส่วนเป็น 0

    # --- 4. สร้าง context เพื่อส่งข้อมูลไปที่ Template ---
    context = {
        'total_balance': total_balance,
        'month_income': month_income,
        'month_expense': month_expense,
        'expense_percentage': expense_percentage
    }
    
    return render(request, "home/home.html", context)


@login_required(login_url="/login/")
def dashboard_today_page(request, user_id):
    user = request.user
    categories = Category.objects.filter(user=user)
    accounts = Account.objects.filter(user=user).order_by("-id")  # ตัวอย่างเรียงล่าสุด
    total_balance = sum(a.balance for a in accounts)

    context = {
        "categories": categories,
        "accounts": accounts,
        "total_balance": total_balance,
    }

    # ส่ง context เข้า render
    return render(request, "home/dashboard.html", context)


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
            "category": t.category_trans,
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
@csrf_exempt
def category_list(request, user_id):
    user = request.user

    if request.method == "POST":
        # Add Category
        category_name = request.POST.get("category_name")
        trans_type = request.POST.get("trans_type")

        if category_name:
            # Avoid duplicate categories
            Category.objects.get_or_create(
                user=user, category_name=category_name, trans_type=trans_type
            )

        # Delete Category
        delete_name = request.POST.get("delete_category_name")

        if delete_name:
            Category.objects.filter(
                user=user, category_name=delete_name, trans_type=trans_type
            ).delete()

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
        # ---- ลบ Category ----
        delete_name = request.POST.get("delete_category_name")
        if delete_name:
            Category.objects.filter(
                user=user_now, category_name=delete_name, trans_type=transaction_type
            ).delete()

        # ---- เพิ่ม Category ----
        add_cat_name = request.POST.get("category_name")
        date_str = request.POST.get("date")
        if add_cat_name and not date_str:
            Category.objects.create(
                user=user_now, category_name=add_cat_name, trans_type=transaction_type
            )

        # ---- เพิ่ม Transaction Income ----
        elif add_cat_name and date_str:
            date = parse_date(date_str)  # convert string to date

            try:
                amount = float(request.POST["amount"])
                if amount <= 0:
                    messages.error(request, "Amount must be positive.")
                    return redirect(
                        reverse("transaction_income", kwargs={"user_id": user_now.id})
                    )

            except ValueError:
                messages.error(request, "Invalid amount format.")
                return redirect(
                    reverse("transaction_income", kwargs={"user_id": user_now.id})
                )

            name_category = add_cat_name
            account_name = request.POST["account"]

            # fetch category from database by user, category_name and type
            category_check = Category.objects.filter(
                user=user_now, category_name=name_category, trans_type=transaction_type
            )

            # fetch account if error then show message
            try:
                account = Account.objects.get(user=user_now, account_name=account_name)
            except ObjectDoesNotExist:
                messages.error(request, "Account not specified.")
                return redirect(
                    reverse("transaction_income", kwargs={"user_id": user_now.id})
                )

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
                category_trans=name_category,
                to_account=account,
            )

            account.balance += float(amount)
            account.save()

        return redirect(
            reverse("transaction_income", kwargs={"user_id": request.user.id})
        )

    categories = Category.objects.filter(user=request.user, trans_type=transaction_type)

    return render(request, "home/transaction_income.html", {"categories": categories})


@login_required(login_url="/login/")
@csrf_exempt
def transaction_expense_page(request, user_id):
    user_now = request.user
    transaction_type = "expense"

    if request.method == "POST":

        # ---- ลบ Category ----
        delete_name = request.POST.get("delete_category_name")
        if delete_name:
            Category.objects.filter(
                user=user_now, category_name=delete_name, trans_type=transaction_type
            ).delete()

        # ---- เพิ่ม Category ----
        add_cat_name = request.POST.get("category_name")
        date_str = request.POST.get("date")
        if add_cat_name and not date_str:
            Category.objects.create(
                user=user_now, category_name=add_cat_name, trans_type=transaction_type
            )

        # ---- เพิ่ม Transaction Expense ----
        elif add_cat_name and date_str:
            date = parse_date(date_str)  # convert string to date

            # Amount must be positive.
            try:
                amount = float(request.POST["amount"])
                if amount <= 0:
                    messages.error(request, "Amount must be positive.")
                    return redirect(
                        reverse("transaction_expense", kwargs={"user_id": user_now.id})
                    )

            # Invalid amount format.
            except ValueError:
                messages.error(request, "Invalid amount format.")
                return redirect(
                    reverse("transaction_expense", kwargs={"user_id": user_now.id})
                )

            name_category = add_cat_name
            account_name = request.POST["account"]

            # fetch category or create if not exist
            category = Category.objects.filter(
                user=user_now, category_name=name_category, trans_type=transaction_type
            ).first() or Category.objects.create(
                user=user_now, category_name=name_category, trans_type=transaction_type
            )

            # fetch account if error then show message
            try:
                account = Account.objects.get(user=user_now, account_name=account_name)
            except ObjectDoesNotExist:
                messages.error(request, "Account not specified.")
                return redirect(
                    reverse("transaction_expense", kwargs={"user_id": user_now.id})
                )

            # create expense
            Expense.objects.create(
                user=user_now,
                trans_type=transaction_type,
                date=date,
                amount=amount,
                category_trans=name_category,
                from_account=account,
            )

            # update account balance
            account.balance -= amount
            account.save()

        # redirect หลัง POST
        return redirect(reverse("transaction_expense", kwargs={"user_id": user_now.id}))

    categories = Category.objects.filter(user=request.user, trans_type=transaction_type)

    return render(request, "home/transaction_expense.html", {"categories": categories})


@login_required(login_url="/login/")
@csrf_exempt
def transaction_transfer_page(request, user_id):
    user_now = request.user
    transaction_type = "transfer"

    if request.method == "POST":
        # ---- ลบ Category ----
        delete_name = request.POST.get("delete_category_name")
        if delete_name:
            Category.objects.filter(
                user=user_now, category_name=delete_name, trans_type=transaction_type
            ).delete()

        # ---- เพิ่ม Category ----
        add_cat_name = request.POST.get("category_name")
        date_str = request.POST.get("date")
        if add_cat_name and not date_str:
            Category.objects.create(
                user=user_now, category_name=add_cat_name, trans_type=transaction_type
            )

        # ---- เพิ่ม Transaction Transfer ----
        elif add_cat_name and date_str:
            date = parse_date(date_str)  # convert string to date

            try:
                amount = float(request.POST["amount"])
                if amount <= 0:
                    messages.error(request, "Amount must be positive.")
                    return redirect(
                        reverse("transaction_transfer", kwargs={"user_id": user_now.id})
                    )

            # Invalid amount format.
            except ValueError:
                messages.error(request, "Invalid amount format.")
                return redirect(
                    reverse("transaction_transfer", kwargs={"user_id": user_now.id})
                )

            name_category = add_cat_name

            from_account = request.POST["from_account"]
            to_account = request.POST["to_account"]

            # fetch category from database by user, category_name and type

            category_check = Category.objects.filter(
                user=user_now, category_name=name_category, trans_type=transaction_type
            )

            # fetch accounts if error then show message
            try:
                from_account = Account.objects.get(
                    user=user_now, account_name=from_account
                )
                to_account = Account.objects.get(user=user_now, account_name=to_account)
            except ObjectDoesNotExist:
                messages.error(
                    request, "Account either not specified or does not exists."
                )
                return redirect(
                    reverse("transaction_transfer", kwargs={"user_id": user_now.id})
                )

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
                trans_type="expense",
                date=date,
                amount=amount,
                category_trans=name_category,
                from_account=from_account,
            )

            income = Income.objects.create(
                user=user_now,
                trans_type="income",
                date=date,
                amount=amount,
                category_trans=name_category,
                to_account=to_account,
            )

            if from_account != to_account:
                from_account.balance -= float(amount)

                from_account.save()

                to_account.balance += float(amount)

                to_account.save()

            return redirect(
                reverse("transaction_transfer", kwargs={"user_id": request.user.id})
            )

    categories = Category.objects.filter(user=request.user, trans_type=transaction_type)

    return render(request, "home/transaction_transfer.html", {"categories": categories})


@login_required(login_url="/login/")
def stats_page(request, user_id):
    """
    View นี้จะทำหน้าที่ render หน้า HTML หลักของ Stats
    และส่งข้อมูลพื้นฐานเช่น ปีที่มี Transaction ไปให้ Template
    """
    user = request.user
    # ดึงปีทั้งหมดที่มีการทำรายการ เพื่อไปสร้างเป็นตัวเลือกใน dropdown
    # เรียงจากปีล่าสุดไปหาเก่าสุด
    years_with_transactions = Transaction.objects.filter(user=user).dates('date', 'year', order='DESC')
    
    # ดึงเดือนและปีทั้งหมดที่มีรายการ expense เพื่อใช้ในหน้า Compare
    expense_months = Expense.objects.filter(user=user) \
        .dates('date', 'month', order='DESC')
        
    context = {
        'years': [d.year for d in years_with_transactions],
        'expense_months': [{'value': d.strftime('%Y-%m'), 'text': d.strftime('%B %Y')} for d in expense_months]
    }
    return render(request, "home/stats.html", context)


@login_required
def stats_summary_api(request):
    """
    API View สำหรับส่งข้อมูล Pie Chart (Income หรือ Expense)
    รับ parameter: ?year=YYYY&month=MM&type=income
    """
    user = request.user
    year = request.GET.get('year')
    month = request.GET.get('month')
    trans_type = request.GET.get('type') # 'income' or 'expense'

    if not all([year, month, trans_type]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    model = Income if trans_type == 'income' else Expense

    # Query ข้อมูลและจัดกลุ่มตาม category
    summary = model.objects.filter(
        user=user,
        date__year=year,
        date__month=month
    ).values('category_trans').annotate(total=Sum('amount')).order_by('-total')

    overall_total = sum(item['total'] for item in summary)

    data = {
        'labels': [item['category_trans'] for item in summary],
        'values': [item['total'] for item in summary],
        'overall_total': overall_total,
    }
    return JsonResponse(data)


@login_required
def stats_yearly_api(request):
    """
    API View สำหรับส่งข้อมูล Line Chart (Statistics)
    รับ parameter: ?year=YYYY
    """
    user = request.user
    year = request.GET.get('year')

    if not year:
        return JsonResponse({'error': 'Year parameter is required'}, status=400)

    income_data = []
    expense_data = []
    month_labels = [calendar.month_name[i] for i in range(1, 13)]

    for month in range(1, 13):
        income_total = Income.objects.filter(
            user=user, date__year=year, date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        expense_total = Expense.objects.filter(
            user=user, date__year=year, date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        income_data.append(income_total)
        expense_data.append(expense_total)
        
    data = {
        'labels': month_labels,
        'income': income_data,
        'expense': expense_data
    }
    return JsonResponse(data)


@login_required(login_url="/login/")
def settings_page(request, user_id):
    return render(request, "home/settings.html")


def contact(request):
    return render(request, "home/contact.html")


