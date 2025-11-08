from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Account, Income, Expense
from django.utils.dateparse import parse_date

class HomeAppTests(TestCase):
    def setUp(self):
        # สร้าง user และ login
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()
        self.client.login(username="testuser", password="password")

        # สร้าง accounts และ categories
        self.account = Account.objects.create(
            user=self.user, account_name="Cash", type_acc="Wallet", balance=1000
        )
        self.account2 = Account.objects.create(
            user=self.user, account_name="Bank", type_acc="Bank", balance=500
        )
        self.cat_income = Category.objects.create(
            user=self.user, category_name="Salary", trans_type="income"
        )
        self.cat_expense = Category.objects.create(
            user=self.user, category_name="Food", trans_type="expense"
        )
        self.cat_transfer = Category.objects.create(
            user=self.user, category_name="Bank Transfer", trans_type="transfer"
        )

    # ----- Landing -----
    def test_landing_redirects_home(self):
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/{self.user.id}/home/", response.url)

    # ----- Home -----
    def test_home_page_loads(self):
        response = self.client.get(reverse("home", kwargs={"user_id": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/home.html")

    # ----- Dashboard -----
    def test_dashboard_context(self):
        response = self.client.get(reverse("dashboard", kwargs={"user_id": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("categories", response.context)
        self.assertIn("accounts", response.context)
        self.assertIn("total_balance", response.context)

    # ----- Transaction Income -----
    def test_transaction_income_post(self):
        response = self.client.post(
            reverse("transaction_income", kwargs={"user_id": self.user.id}),
            data={
                "date": "2025-11-08",
                "amount": "500",
                "category_name": "Salary",
                "account": "Cash",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 1500)
        income = Income.objects.filter(user=self.user, amount=500).first()
        self.assertIsNotNone(income)

    # ----- Transaction Expense -----
    def test_transaction_expense_post(self):
        response = self.client.post(
            reverse("transaction_expense", kwargs={"user_id": self.user.id}),
            data={
                "date": "2025-11-08",
                "amount": "200",
                "category_name": "Food",
                "account": "Cash",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 800)
        expense = Expense.objects.filter(user=self.user, amount=200).first()
        self.assertIsNotNone(expense)

    # ----- Transaction Transfer -----
    def test_transaction_transfer_post(self):
        response = self.client.post(
            reverse("transaction_transfer", kwargs={"user_id": self.user.id}),
            data={
                "date": "2025-11-08",
                "amount": "300",
                "category_name": "Bank Transfer",
                "from_account": "Cash",
                "to_account": "Bank",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.account.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(self.account.balance, 700)  # Cash ลดลง
        self.assertEqual(self.account2.balance, 800)  # Bank เพิ่มขึ้น

    # ----- Transaction Transfer -----
    def test_transaction_transfer_new_category(self):
        response = self.client.post(
            reverse("transaction_transfer", kwargs={"user_id": self.user.id}),
            data={
                "date": "2025-11-08",
                "amount": "400",
                "category_name": "NewTransferCat",
                "from_account": "Cash",
                "to_account": "Bank",
            },
        )
        self.assertTrue(Category.objects.filter(user=self.user, category_name="NewTransferCat").exists())


    # ----- Category List -----
    def test_category_add_delete(self):
        # เพิ่ม category
        response = self.client.post(
            reverse("category_list", kwargs={"user_id": self.user.id}),
            data={"category_name": "NewCat"},
        )
        self.assertTrue(Category.objects.filter(user=self.user, category_name="NewCat").exists())

        # ลบ category
        response = self.client.post(
            reverse("category_list", kwargs={"user_id": self.user.id}),
            data={"delete_category_name": "NewCat"},
        )
        self.assertFalse(Category.objects.filter(user=self.user, category_name="NewCat").exists())

    # ----- Stats Page -----
    def test_stats_page_loads(self):
        response = self.client.get(reverse("stats", kwargs={"user_id": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/stats.html")

    # ----- Settings Page -----
    def test_settings_page_loads(self):
        response = self.client.get(reverse("settings", kwargs={"user_id": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/settings.html")

    # ----- Spending API -----
    def test_spending_api_daily(self):
        Income.objects.create(
            user=self.user,
            trans_type="income",
            date="2025-11-08",
            amount=500,
            category=self.cat_income,
            to_account=self.account,
        )
        response = self.client.get(reverse("spending_api") + "?mode=daily&date=2025-11-08")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["spendings"]), 1)
        self.assertEqual(data["spendings"][0]["amount"], 500)

    # ----- Accounts API -----
    def test_accounts_api(self):
        response = self.client.get(reverse("accounts_api"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_balance"], self.account.balance + self.account2.balance)
        self.assertEqual(len(data["accounts"]), 2)
        self.assertEqual(data["accounts"][0]["name"], "Bank")  # เรียง id desc


    # ----- Transaction Income: POST ไม่มี date -----
    def test_transaction_income_post_no_date(self):
        response = self.client.post(
            reverse("transaction_income", kwargs={"user_id": self.user.id}),
            data={"category_name": "Salary"}
        )
        self.assertEqual(response.status_code, 302)  # ตรวจสอบ redirect
        self.assertIn(reverse("transaction_income", kwargs={"user_id": self.user.id}), response.url)

    # ----- Transaction Transfer: POST ไม่มี date -----
    def test_transaction_transfer_post_no_date(self):
        response = self.client.post(
            reverse("transaction_transfer", kwargs={"user_id": self.user.id}),
            data={
                "category_name": "Bank Transfer",
                "from_account": "Cash",
                "to_account": "Bank"
            }
        )
        self.assertEqual(response.status_code, 302)  # ตรวจสอบ redirect
        self.assertIn(reverse("transaction_transfer", kwargs={"user_id": self.user.id}), response.url)


    # ----- Transaction Expense: test branch add category only (no date) -----
    def test_transaction_expense_add_category_only(self):
        response = self.client.post(
            reverse("transaction_expense", kwargs={"user_id": self.user.id}),
            data={"category_name": "NewExpenseCat"}
        )
        self.assertTrue(
            Category.objects.filter(user=self.user, category_name="NewExpenseCat", trans_type="expense").exists()
        )

    # ----- Category List: test GET request -----
    def test_category_list_get(self):
        response = self.client.get(reverse("category_list", kwargs={"user_id": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/category_list.html")
        self.assertIn("categories", response.context)
        self.assertGreaterEqual(len(response.context["categories"]), 1)

    # ----- Spending API: test monthly and yearly -----
    def test_spending_api_monthly(self):
        Income.objects.create(
            user=self.user,
            trans_type="income",
            date="2025-11-08",
            amount=500,
            category=self.cat_income,
            to_account=self.account,
        )
        response = self.client.get(reverse("spending_api") + "?mode=monthly&month=2025-11")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data["spendings"]), 1)

    def test_spending_api_yearly(self):
        Income.objects.create(
            user=self.user,
            trans_type="income",
            date="2025-11-08",
            amount=500,
            category=self.cat_income,
            to_account=self.account,
        )
        response = self.client.get(reverse("spending_api") + "?mode=yearly&year=2025")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data["spendings"]), 1)

    def test_transaction_income_post_no_date(self):
        response = self.client.post(
            reverse("transaction_income", kwargs={"user_id": self.user.id}),
            data={"amount": "500", "category_name": "Salary", "account": "Cash"},
        )
        self.assertEqual(response.status_code, 302)  # ตรวจสอบ redirect

    def test_transaction_transfer_post_no_date(self):
        response = self.client.post(
            reverse("transaction_transfer", kwargs={"user_id": self.user.id}),
            data={"amount": "300", "category_name": "Bank Transfer",
                "from_account": "Cash", "to_account": "Bank"},
        )
        self.assertEqual(response.status_code, 302)

    def test_transaction_expense_delete_category(self):
        Category.objects.create(user=self.user, category_name="TempCat", trans_type="expense")
        response = self.client.post(
            reverse("transaction_expense", kwargs={"user_id": self.user.id}),
            data={"delete_category_name": "TempCat"}
        )
        self.assertFalse(Category.objects.filter(user=self.user, category_name="TempCat").exists())


