from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("home/", views.home_page, name="home"),
    path("dashboard/", views.dashboard_today_page, name="dashboard"),
    path(
        "transaction/income/", views.transaction_income_page, name="transaction_income"
    ),
    path(
        "transaction/expense/",
        views.transaction_expense_page,
        name="transaction_expense",
    ),
    path(
        "transaction/transfer/",
        views.transaction_transfer_page,
        name="transaction_transfer",
    ),
    path("stats/", views.stats_page, name="stats"),
    path("settings/", views.settings_page, name="settings"),
]
