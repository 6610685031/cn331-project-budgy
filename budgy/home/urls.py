from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("<int:user_id>/home/", views.home_page, name="home"),
    path("<int:user_id>/dashboard/", views.dashboard_today_page, name="dashboard"),
    path(
        "<int:user_id>/transaction/income/",
        views.transaction_income_page,
        name="transaction_income",
    ),
    path(
        "<int:user_id>/transaction/expense/",
        views.transaction_expense_page,
        name="transaction_expense",
    ),
    path(
        "<int:user_id>/transaction/transfer/",
        views.transaction_transfer_page,
        name="transaction_transfer",
    ),
    path("<int:user_id>/stats/", views.stats_page, name="stats"),
    path("<int:user_id>/settings/", views.settings_page, name="settings"),
    path("edit/category/", views.category_list, name="category_list"),
    re_path(r"^([a-zA-Z]+)/$", views.landing_page, name="landing"),
]
