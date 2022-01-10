from django.urls import path
from django.views.generic import TemplateView
from expensesapp.views import HomeView, ManagerView, ProfileView, SettingsView

app_name = "expensesapp"
urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("manager/", ManagerView.as_view(), name="manager"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("settings/", SettingsView.as_view(), name="settings"),
]
