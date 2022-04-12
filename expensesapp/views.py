from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from expensesapp.models import *
from expensesapp.forms import *


class ManagerView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/manager.html"


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/settings.html"


class AccessDeniedView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/access_denied.html"


@login_required
def home_view(request):
    claim_list = Claim.objects.filter(owner=request.user)
    return render(request, "expensesapp/home.html", {"claim_list": claim_list})


@login_required
def claim_new_view(request):
    currencies = Currency.objects.all().order_by("name")
    default_currency = request.user.default_currency
    if request.method == "POST":
        claim_new_form = ClaimNewForm(request.POST, all_currencies=currencies, default_currency=default_currency)
        if claim_new_form.is_valid():
            currency = Currency.objects.get(name=claim_new_form.cleaned_data['currency'])
            description = claim_new_form.cleaned_data['description']
            new_claim = Claim.create(request.user, currency, description)
            new_claim.save()
            return HttpResponseRedirect("/claims/"+str(new_claim.reference))
    else:
        claim_new_form = ClaimNewForm(all_currencies=currencies, default_currency=default_currency)
    return render(request, "expensesapp/claim_new.html", {"claim_new_form": claim_new_form})


@login_required
def claim_details_view(request, claim_ref):
    # Check that the claim exists
    try:
        claim = Claim.objects.get(reference=claim_ref)
    except Claim.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has access to view this claim
    if not claim.user_can_access(request.user):
        return render(request, "expensesapp/access_denied.html")

    claim_delete_form = ClaimDeleteForm(claim_ref=claim_ref)
    return render(request, "expensesapp/claim_details.html", {"claim": claim, "claim_delete_form": claim_delete_form})


@login_required
def claim_edit_view(request, claim_ref):

    # Check that the claim exists
    try:
        claim = Claim.objects.get(reference=claim_ref)
    except Claim.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has access to view this claim
    if not claim.user_can_access(request.user):
        return render(request, "expensesapp/access_denied.html")

    if request.method == "POST":
        claim_edit_form = ClaimEditForm(request.POST, description=claim.description)
        if claim_edit_form.is_valid():
            replacement_desc = claim_edit_form.cleaned_data['description']
            claim.description = replacement_desc
            claim.save()
            return HttpResponseRedirect("/claims/" + claim.reference)
    else:
        claim_edit_form = ClaimEditForm(description=claim.description)
    return render(request, "expensesapp/claim_edit.html", {"claim_edit_form": claim_edit_form, "claim": claim})


@login_required
def claim_delete_view(request, claim_ref):

    # Check that the claim exists
    try:
        claim = Claim.objects.get(reference=claim_ref)
    except Claim.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has access to view this claim
    if not claim.user_can_access(request.user):
        return render(request, "expensesapp/access_denied.html")

    if request.method == "POST":
        claim_delete_form = ClaimDeleteForm(request.POST, claim_ref=claim_ref)
        if claim_delete_form.is_valid():
            claim.delete()
            return HttpResponseRedirect("/")


@login_required
def receipt_new_view(request, claim_ref):

    # Check that the claim exists
    try:
        claim = Claim.objects.get(reference=claim_ref)
    except Claim.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has access to view this claim
    if not claim.user_can_access(request.user):
        return render(request, "expensesapp/access_denied.html")

    categories = Category.objects.all().order_by("name")
    if request.method == "POST":
        receipt_new_form = ReceiptNewForm(request.POST, claim_ref=claim_ref, categories=categories)
        if receipt_new_form.is_valid():
            claim = Claim.objects.get(reference=receipt_new_form.cleaned_data["claim"])
            category = Category.objects.get(name=receipt_new_form.cleaned_data["category"])
            date_incurred = receipt_new_form.cleaned_data["date_incurred"]
            amount = receipt_new_form.cleaned_data["amount"]
            vat = receipt_new_form.cleaned_data["vat"]
            description = receipt_new_form.cleaned_data["description"]
            new_receipt = Receipt.create(claim, category, date_incurred, amount, vat, description)
            new_receipt.save()
            return HttpResponseRedirect("/claims/"+str(claim.reference))
    else:
        receipt_new_form = ReceiptNewForm(claim_ref=claim_ref, categories=categories)
    return render(request, "expensesapp/receipt_new.html", {"claim": claim, "receipt_new_form": receipt_new_form})


@login_required
def receipt_details_view(request, receipt_ref):

    # Check that the receipt exists
    try:
        receipt = Receipt.objects.get(reference=receipt_ref)
    except Receipt.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has access to view this receipt
    if not receipt.user_can_access(request.user):
        return render(request, "expensesapp/access_denied.html")

    receipt_delete_form = ReceiptDeleteForm(receipt_ref=receipt_ref)
    return render(request, "expensesapp/receipt_details.html", {"receipt": receipt,
                                                                "receipt_delete_form": receipt_delete_form})


@login_required
def receipt_edit_view(request, receipt_ref):

    # Check that the receipt exists
    try:
        receipt = Receipt.objects.get(reference=receipt_ref)
    except Receipt.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has access to view this receipt
    if not receipt.user_can_access(request.user):
        return render(request, "expensesapp/access_denied.html")

    categories = Category.objects.all().order_by("name")
    if request.method == "POST":
        receipt_edit_form = ReceiptEditForm(request.POST, categories=categories, date_incurred=receipt.date_incurred,
                                            category=receipt.category, amount=receipt.amount, vat=receipt.vat,
                                            description=receipt.description)
        if receipt_edit_form.is_valid():
            new_date_incurred = receipt_edit_form.cleaned_data["date_incurred"]
            receipt.date_incurred = new_date_incurred
            new_category = receipt_edit_form.cleaned_data["category"]
            receipt.category = Category.objects.get(name=new_category)
            new_amount = receipt_edit_form.cleaned_data["amount"]
            receipt.amount = new_amount
            new_vat = receipt_edit_form.cleaned_data["vat"]
            receipt.vat = new_vat
            new_description = receipt_edit_form.cleaned_data["description"]
            receipt.description = new_description
            receipt.save()
            return HttpResponseRedirect("/receipts/" + receipt.reference)
    else:
        receipt_edit_form = ReceiptEditForm(categories=categories, date_incurred=receipt.date_incurred,
                                            category=receipt.category, amount=receipt.amount, vat=receipt.vat,
                                            description=receipt.description)
    return render(request, "expensesapp/receipt_edit.html", {"receipt_edit_form": receipt_edit_form, "receipt": receipt})


@login_required
def receipt_delete_view(request, receipt_ref):

    # Check that the receipt exists
    try:
        receipt = Receipt.objects.get(reference=receipt_ref)
    except Receipt.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has access to view this receipt
    if not receipt.user_can_access(request.user):
        return render(request, "expensesapp/access_denied.html")


@login_required
def receipt_delete_view(request, receipt_ref):

    # Check that the receipt exists
    try:
        receipt = Receipt.objects.get(reference=receipt_ref)
    except Receipt.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has access to view this receipt
    if not receipt.user_can_access(request.user):
        return render(request, "expensesapp/access_denied.html")

    if request.method == "POST":
        receipt_delete_form = ReceiptDeleteForm(request.POST, receipt_ref=receipt_ref)
        if receipt_delete_form.is_valid():
            parent_claim_ref = receipt.claim.reference
            receipt.delete()
            return HttpResponseRedirect(reverse("expensesapp:claim_details", args=[parent_claim_ref]))
