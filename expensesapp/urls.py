from django.urls import path
from django.views.generic import TemplateView

app_name = "expensesapp"
urlpatterns = [
    path("home/", TemplateView.as_view(template_name="expensesapp/home.html"), name="home"),
    path("manager/", TemplateView.as_view(template_name="expensesapp/manager.html"), name="manager"),
    path("profile/", TemplateView.as_view(template_name="expensesapp/profile.html"), name="profile"),
    path("settings/", TemplateView.as_view(template_name="expensesapp/settings.html"), name="settings"),
]
