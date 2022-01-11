from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, DetailView, ListView
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


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/settings.html"


class ClaimView(LoginRequiredMixin, DetailView, ):
    template_name = "expensesapp/claim.html"
    model = Claim


def new_claim_view(request):
    if request.method == "POST":
        form = NewClaimForm(request.POST)
        if form.is_valid():
            new_claim = Claim.create(request.user, form.cleaned_data['description'])
            new_claim.save()
            return HttpResponseRedirect("/claims/"+str(new_claim.id))
    else:
        form = NewClaimForm()
    return render(request, "expensesapp/new_claim.html", {"form": form})


def home_redirect_view(request):
    return redirect("/home/")

