from django.urls import path
from . import views

app_name = "expensesapp"
urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("", views.home_redirect_view),
    path("manager/", views.ManagerView.as_view(), name="manager"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("new-claim/", views.claim_new_view, name="claim_new"),
    path("claims/<int:pk>/", views.ClaimView.as_view(), name="claim"),
    path("claims/<int:claim_id>/edit/", views.claim_edit_view, name="claim_edit")
]
