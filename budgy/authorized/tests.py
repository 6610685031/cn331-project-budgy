from django.test import TestCase

# authorized/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from home.models import Account


class AuthorizedViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # สร้าง user ตัวอย่าง
        self.user = User.objects.create_user(username="testuser", password="testpass")
        Account.objects.create(
            user=self.user, account_name="Cash", type_acc="cash", balance=0.0
        )

    # -------------------- LOGIN --------------------
    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authorized/login.html")

    def test_login_success(self):
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": "testpass"},
            follow=True,
        )
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertRedirects(
            response, reverse("home", kwargs={"user_id": self.user.id})
        )

    def test_login_invalid_user(self):
        response = self.client.post(
            reverse("login"),
            {"username": "wronguser", "password": "wrongpass"},
            follow=True,
        )
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertContains(response, "This user is not registry yet")

    def test_login_already_authenticated(self):
        # Login ก่อนทดสอบ
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("login"), follow=True)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertRedirects(
            response, reverse("home", kwargs={"user_id": self.user.id})
        )

    # -------------------- LOGOUT --------------------
    def test_logout_redirects(self):
        # Login ก่อน logout
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("logout"), follow=True)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertRedirects(response, reverse("login"))

    # -------------------- REGISTER --------------------
    def test_register_page_loads(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authorized/register.html")

    def test_register_success(self):
        response = self.client.post(
            reverse("register"),
            {
                "Username": "newuser",
                "Password": "newpass",
                "confirm_password": "newpass",
                "email": "newuser@test.com",
            },
            follow=True,
        )
        self.assertTrue(User.objects.filter(username="newuser").exists())
        new_user = User.objects.get(username="newuser")
        self.assertTrue(
            Account.objects.filter(user=new_user, account_name="Cash").exists()
        )
        self.assertTemplateUsed(response, "authorized/login.html")
        self.assertContains(response, "Register success")

    def test_register_password_mismatch(self):
        response = self.client.post(
            reverse("register"),
            {
                "Username": "user2",
                "Password": "pass1",
                "confirm_password": "pass2",
                "email": "user2@test.com",
            },
        )
        self.assertContains(response, "Password not match, Please try again.")
        self.assertFalse(User.objects.filter(username="user2").exists())

    def test_register_duplicate_username(self):
        response = self.client.post(
            reverse("register"),
            {
                "Username": "testuser",
                "Password": "testpass",
                "confirm_password": "testpass",
                "email": "duplicate@test.com",
            },
        )
        self.assertContains(
            response, "This Username already registry, Please try again."
        )

    def test_register_already_authenticated(self):
        # Login ก่อนทดสอบ
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("register"), follow=True)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertRedirects(
            response, reverse("home", kwargs={"user_id": self.user.id})
        )
