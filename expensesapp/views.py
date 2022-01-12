from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from expensesapp.models import Claim
from expensesapp.forms import ClaimNewForm, ClaimEditForm


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
    template_name = "expensesapp/claim_details.html"
    model = Claim


def claim_new_view(request):
    if request.method == "POST":
        form = ClaimNewForm(request.POST)
        if form.is_valid():
            new_claim = Claim.create(request.user, form.cleaned_data['description'])
            new_claim.save()
            return HttpResponseRedirect("/claims/"+str(new_claim.id))
    else:
        form = ClaimNewForm()
    return render(request, "expensesapp/claim_new.html", {"form": form})


def claim_edit_view(request, claim_id):
    claim = get_object_or_404(Claim, pk=claim_id)
    if request.method == "POST":
        form = ClaimEditForm(request.POST)
        if form.is_valid():
            replacement_desc = form.cleaned_data['description']
            claim.description = replacement_desc
            claim.save()
            return HttpResponseRedirect("/claims/"+str(claim.id))
    else:
        form = ClaimEditForm()
    return render(request, "expensesapp/claim_edit.html", {"form": form, "claim": claim})



def home_redirect_view(request):
    return redirect("/home/")

