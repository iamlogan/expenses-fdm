from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/home.html"


class ManagerView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/manager.html"


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/profile.html"


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/settings.html"
