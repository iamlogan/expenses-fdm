from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from expensesapp.models import Claim
from expensesapp.forms import NewClaimForm


class HomeView(LoginRequiredMixin, ListView):
    template_name = "expensesapp/home.html"
    context_object_name = "claim_list"

    def get_queryset(self):
        return Claim.objects.filter(owner=self.request.user).order_by("-creation_datetime")


class ManagerView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/manager.html"


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/profile.html"


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/settings.html"


def new_claim_view(request):
    if request.method == "POST":
        form = NewClaimForm(request.POST)
        if form.is_valid():
            new_claim = Claim.create(request.user, form.cleaned_data['description'])
            new_claim.save()
            return HttpResponseRedirect("/home/")
    else:
        form = NewClaimForm()
    return render(request, "expensesapp/new_claim.html", {"form": form})


def home_redirect_view(request):
    return redirect("/home/")

