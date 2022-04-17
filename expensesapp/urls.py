from django.urls import path
from . import views

app_name = "expensesapp"
urlpatterns = [
    path("", views.home_view, name="home"),
    path("account/", views.account_details_view, name="account_details"),
    path("account/edit/", views.account_edit_view, name="account_edit"),
    path("claims/new/", views.claim_new_view, name="claim_new"),
    path("claims/<str:claim_ref>/", views.claim_details_view, name="claim_details"),
    path("claims/<str:claim_ref>/edit/", views.claim_edit_view, name="claim_edit"),
    path("claims/<str:claim_ref>/delete/", views.claim_delete_view, name="claim_delete"),
    path("claims/<str:claim_ref>/new-receipt", views.receipt_new_view, name="receipt_new"),
    path("receipts/<str:receipt_ref>/", views.receipt_details_view, name="receipt_details"),
    path("receipts/<str:receipt_ref>/edit/", views.receipt_edit_view, name="receipt_edit"),
    path("receipts/<str:receipt_ref>/delete/", views.receipt_delete_view, name="receipt_delete"),
    path("claims/<str:claim_ref>/submit/", views.claim_submit_view, name="claim_submit"),
    path("your-expenses/<str:category>/<int:page_num>/", views.your_expenses_view, name="your_expenses"),
    path("manager/<str:group_url>/<int:page_num>/", views.manager_view, name="manager"),
    path("claims/<str:claim_ref>/return/", views.claim_return_view, name="claim_return"),
    path("claims/<str:claim_ref>/approve/", views.claim_approve_view, name="claim_approve"),
    path("back/", views.back_view, name="back"),
]
