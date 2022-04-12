from django.urls import path
from . import views

app_name = "expensesapp"
urlpatterns = [
    path("", views.home_view, name="home"),
    path("manager/", views.ManagerView.as_view(), name="manager"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("claims/new/", views.claim_new_view, name="claim_new"),
    path("claims/<str:claim_ref>/", views.claim_details_view, name="claim_details"),
    path("claims/<str:claim_ref>/edit/", views.claim_edit_view, name="claim_edit"),
    path("claims/<str:claim_ref>/delete/", views.claim_delete_view, name="claim_delete"),
    path("claims/<str:claim_ref>/new-receipt", views.receipt_new_view, name="receipt_new"),
    path("receipts/<str:receipt_ref>/", views.receipt_details_view, name="receipt_details"),
    path("receipts/<str:receipt_ref>/edit/", views.receipt_edit_view, name="receipt_edit"),
    path("receipts/<str:receipt_ref>/delete/", views.receipt_delete_view, name="receipt_delete"),
]
