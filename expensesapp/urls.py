from django.urls import path
from expensesapp.views import HomeView, ManagerView, ProfileView, SettingsView, home_redirect_view, new_claim_view

app_name = "expensesapp"
urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("", home_redirect_view),
    path("manager/", ManagerView.as_view(), name="manager"),
    path("settings/", SettingsView.as_view(), name="settings"),
    path("new-claim/", new_claim_view, name="new_claim"),
]
