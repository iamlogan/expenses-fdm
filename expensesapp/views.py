import math

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from expensesapp.models import *
from expensesapp.forms import *


class AccessDeniedView(LoginRequiredMixin, TemplateView):
    template_name = "expensesapp/access_denied.html"


@login_required
def home_view(request):
    return HttpResponseRedirect(reverse("expensesapp:your_expenses", args=["all", 1]))


@login_required
def account_details_view(request):
    return render(request, "expensesapp/account_details.html")


@login_required
def account_edit_view(request):
    default_currency = request.user.default_currency
    substitute = request.user.substitute
    if substitute:
        substitute_email = substitute.email
    else:
        substitute_email = None
    if request.method == "POST":
        account_edit_form = AccountEditForm(request.POST,default_currency=default_currency,
                                            substitute_email=substitute_email)
        if account_edit_form.is_valid():
            new_default_currency = Currency.objects.get(name=account_edit_form.cleaned_data["default_currency"])
            request.user.default_currency = new_default_currency
            new_substitute_email = account_edit_form.cleaned_data["substitute_email"]
            if new_substitute_email:
                request.user.substitute = User.objects.get(email=new_substitute_email)
            else:
                request.user.substitute = None
            request.user.save()
            return HttpResponseRedirect(reverse("expensesapp:account_details"))
    else:
        account_edit_form = AccountEditForm(default_currency=default_currency, substitute_email=substitute_email)
    return render(request, "expensesapp/account_edit.html", {"account_edit_form": account_edit_form})


@login_required
def claim_new_view(request):
    default_currency = request.user.default_currency
    if request.method == "POST":
        claim_new_form = ClaimNewForm(request.POST, default_currency=default_currency)
        if claim_new_form.is_valid():
            currency = Currency.objects.get(name=claim_new_form.cleaned_data['currency'])
            description = claim_new_form.cleaned_data['description']
            new_claim = Claim.create(request.user, currency, description)
            new_claim.save()
            return HttpResponseRedirect(reverse("expensesapp:claim_details", args=[new_claim.reference]))
    else:
        claim_new_form = ClaimNewForm(default_currency=default_currency)
    return render(request, "expensesapp/claim_new.html", {"claim_new_form": claim_new_form})


@login_required
def claim_details_view(request, claim_ref):

    # Check that the claim exists
    try:
        claim = Claim.objects.get(reference=claim_ref)
    except Claim.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has permission to access this claim
    if not claim.user_can_view(request.user):
        return render(request, "expensesapp/access_denied.html")

    claim_delete_form = ClaimDeleteForm(claim_ref=claim_ref)
    claim_submit_form = ClaimSubmitForm(claim_ref=claim_ref)
    all_teams_pending_claims = request.user.get_all_teams_pending_claims()
    if all_teams_pending_claims:
        if (claim.status == "2") and (claim in request.user.get_all_teams_pending_claims()):
            claim_return_form = ClaimReturnForm()
            claim_approve_form = ClaimApproveForm(claim_ref=claim_ref)
        else:
            claim_return_form = None
            claim_approve_form = None
    else:
        claim_return_form = None
        claim_approve_form = None
    return render(request, "expensesapp/claim_details.html", {"claim": claim, "claim_delete_form": claim_delete_form,
                                                              "claim_submit_form": claim_submit_form,
                                                              "claim_return_form": claim_return_form,
                                                              "claim_approve_form": claim_approve_form})


@login_required
def claim_edit_view(request, claim_ref):

    # Check that the claim exists
    try:
        claim = Claim.objects.get(reference=claim_ref)
    except Claim.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has permission to edit this claim (only the owner has this permission)
    if not claim.owner == request.user:
        return render(request, "expensesapp/access_denied.html")

    # Check that claim status is editable
    if not claim.is_editable():
        return render(request, "expensesapp/access_denied.html")

    if request.method == "POST":
        claim_edit_form = ClaimEditForm(request.POST, description=claim.description)
        if claim_edit_form.is_valid():
            replacement_desc = claim_edit_form.cleaned_data['description']
            claim.description = replacement_desc
            claim.save()
            return HttpResponseRedirect(reverse("expensesapp:claim_details", args=[claim.reference]))
    else:
        claim_edit_form = ClaimEditForm(description=claim.description)
    return render(request, "expensesapp/claim_edit.html", {"claim": claim, "claim_edit_form": claim_edit_form})


@login_required
def claim_delete_view(request, claim_ref):

    # Check that the claim exists
    try:
        claim = Claim.objects.get(reference=claim_ref)
    except Claim.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has permission to delete this claim (only the owner has this permission)
    if not claim.owner == request.user:
        return render(request, "expensesapp/access_denied.html")

    # Check that claim status is editable
    if not claim.is_editable():
        return render(request, "expensesapp/access_denied.html")

    if request.method == "POST":
        claim_delete_form = ClaimDeleteForm(request.POST, claim_ref=claim_ref)
        if claim_delete_form.is_valid():
            claim.delete()
            return HttpResponseRedirect(reverse("expensesapp:home"))
    return render(request, "expensesapp/access_denied.html")


@login_required
def receipt_new_view(request, claim_ref):

    # Check that the claim exists
    try:
        claim = Claim.objects.get(reference=claim_ref)
    except Claim.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has permission to add a receipt to this claim (only the owner has this permission)
    if not claim.owner == request.user:
        return render(request, "expensesapp/access_denied.html")

    # Check that claim status is editable
    if not claim.is_editable():
        return render(request, "expensesapp/access_denied.html")

    categories = Category.objects.order_by("name")
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
            return HttpResponseRedirect(reverse("expensesapp:claim_details", args=[claim.reference]))
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

    # Check that user has permission to access this receipt
    if not receipt.user_can_view(request.user):
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

    # Check that user has permission to edit this receipt (only the owner has this permission)
    if not receipt.claim.owner == request.user:
        return render(request, "expensesapp/access_denied.html")

    # Check that claim status is editable
    if not receipt.claim.is_editable():
        return render(request, "expensesapp/access_denied.html")

    categories = Category.objects.order_by("name")
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
            return HttpResponseRedirect(reverse("expensesapp:receipt_details", args=[receipt.reference]))
    else:
        receipt_edit_form = ReceiptEditForm(categories=categories, date_incurred=receipt.date_incurred,
                                            category=receipt.category, amount=receipt.amount, vat=receipt.vat,
                                            description=receipt.description)
    return render(request, "expensesapp/receipt_edit.html", {"receipt": receipt,
                                                             "receipt_edit_form": receipt_edit_form})


@login_required
def receipt_delete_view(request, receipt_ref):

    # Check that the receipt exists
    try:
        receipt = Receipt.objects.get(reference=receipt_ref)
    except Receipt.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has permission to delete this receipt (only the owner has this permission)
    if not receipt.claim.owner == request.user:
        return render(request, "expensesapp/access_denied.html")

    # Check that claim status is editable
    if not receipt.claim.is_editable():
        return render(request, "expensesapp/access_denied.html")

    if request.method == "POST":
        receipt_delete_form = ReceiptDeleteForm(request.POST, receipt_ref=receipt.reference)
        if receipt_delete_form.is_valid():
            parent_claim_ref = receipt.claim.reference
            receipt.delete()
            return HttpResponseRedirect(reverse("expensesapp:claim_details", args=[parent_claim_ref]))
    return render(request, "expensesapp/access_denied.html")


@login_required
def claim_submit_view(request, claim_ref):

    # Check that the claim exists
    try:
        claim = Claim.objects.get(reference=claim_ref)
    except Claim.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that user has permission to submit this claim (only the owner has this permission)
    if not claim.owner == request.user:
        return render(request, "expensesapp/access_denied.html")

    # Check that claim status is editable
    if not claim.is_editable():
        return render(request, "expensesapp/access_denied.html")

    if request.method == "POST":
        claim_submit_form = ClaimSubmitForm(request.POST, claim_ref=claim_ref)
        if claim_submit_form.is_valid():
            claim.submit()
            claim.save()
            return HttpResponseRedirect(reverse("expensesapp:claim_details", args=[claim.reference]))
    return render(request, "expensesapp/access_denied.html")


@login_required
def your_expenses_view(request, category, page_num):

    # Filter the users claims by selected category
    if category == "all":
        selected_claims = request.user.claims.all()
    else:
        status_number = None
        for status in Claim.STATUSES:
            if status[1].lower() == category:
                status_number = status[0]
        if status_number:
            selected_claims = request.user.claims.filter(status=status_number)
        else:
            return render(request, "expensesapp/access_denied.html")

    # Filter the queryset of claims to show items based on page number (10 per page)
    items_shown_per_page = 15
    range_min = (page_num * items_shown_per_page) - items_shown_per_page + 1
    range_max = page_num * items_shown_per_page
    total_count = len(selected_claims)
    # There are no claims
    if total_count == 0:
        if page_num == 1:
            claim_list = []
        else:
            return HttpResponseRedirect(reverse("expensesapp:your_expenses", args=[category, 1]))
    # No claims are in range
    elif total_count < range_min:
        if total_count >= range_min - items_shown_per_page:
            return HttpResponseRedirect(reverse("expensesapp:your_expenses", args=[category, page_num - 1]))
        else:
            return HttpResponseRedirect(reverse("expensesapp:your_expenses", args=[category, 1]))
    # 10 claims are in range
    elif total_count >= range_max:
        status_update_datetime_min = selected_claims.order_by("-status_update_datetime")[
            range_min - 1].status_update_datetime
        status_update_datetime_max = selected_claims.order_by("-status_update_datetime")[
            range_max - 1].status_update_datetime
        claim_list = selected_claims.filter(status_update_datetime__gte=status_update_datetime_max).filter(
            status_update_datetime__lte=status_update_datetime_min).order_by("-status_update_datetime")
    # 1 to 9 claims are in range
    else:
        status_update_datetime_min = selected_claims.order_by("-status_update_datetime")[
            range_min - 1].status_update_datetime
        claim_list = selected_claims.filter(status_update_datetime__lte=status_update_datetime_min).order_by(
            "-status_update_datetime")

    # Get data for pagination
    max_pages = math.ceil(total_count / items_shown_per_page)
    clickable_pages = []
    newest_page = False
    oldest_page = False
    previous_page = False
    next_page = False
    for page in range(1, max_pages + 1):
        if (page_num - 2) <= page <= (page_num + 2):
            clickable_pages.append(page)
            if page == page_num - 1:
                previous_page = page
            elif page == page_num + 1:
                next_page = page
        else:
            if page == 1:
                newest_page = page
            if page == max_pages:
                oldest_page = page
    if clickable_pages == [1]:
        clickable_pages = None

    # Get URL info for back_view
    request.user.back_url = ",".join(["expensesapp:your_expenses", category, str(page_num)])
    request.user.save()

    claim_categories = [{"name": "All", "count": len(request.user.claims.all())}]
    for status in Claim.STATUSES:
        claim_categories.append({"name": status[1], "count": len(request.user.claims.filter(status=status[0]))})
    return render(request, "expensesapp/your_expenses.html", {"claim_list": claim_list,
                                                              "claim_categories": claim_categories,
                                                              "category": category,
                                                              "current_page": page_num,
                                                              "clickable_pages": clickable_pages,
                                                              "newest_page": newest_page,
                                                              "oldest_page": oldest_page,
                                                              "previous_page": previous_page,
                                                              "next_page": next_page})


@login_required
def manager_view(request, group_url, page_num):

    # Check that user is a manager
    if not request.user.is_manager():
        return render(request, "expensesapp/access_denied.html")

    # Get claims in the users team
    your_teams_claims = request.user.get_your_teams_pending_claims()
    if your_teams_claims:
        your_teams_claims_len = len(your_teams_claims)
    else:
        your_teams_claims_len = 0

    # Get claims in other teams
    other_teams_claims = request.user.get_other_teams_pending_claims()
    if other_teams_claims:
        other_teams_claims_len = len(other_teams_claims)
    else:
        other_teams_claims_len = 0

    # Filter the team members' claims by selected category
    if group_url == "your-team":
        selected_claims = your_teams_claims
        group_name = "your team"
    elif group_url == "other-teams":
        selected_claims = other_teams_claims
        group_name = "other teams"
    else:
        return render(request, "expensesapp/access_denied.html")
    if selected_claims:
        selected_claims = selected_claims.order_by("submission_datetime")

    # Filter the queryset of claims to show items based on page number (10 per page)
    items_shown_per_page = 15
    range_min = (page_num * items_shown_per_page) - items_shown_per_page + 1
    range_max = page_num * items_shown_per_page
    if selected_claims:
        total_count = len(selected_claims)
    else:
        total_count = 0
    if total_count == 0:  # No claims at all
        if page_num == 1:
            claim_list = []
        else:
            return HttpResponseRedirect(reverse("expensesapp:manager", args=[group_url, 1]))
    elif total_count < range_min:  # No claims are in range
        if total_count >= range_min - items_shown_per_page:
            return HttpResponseRedirect(reverse("expensesapp:manager", args=[group_url, page_num - 1]))
        else:
            return HttpResponseRedirect(reverse("expensesapp:manager", args=[group_url, 1]))
    elif total_count >= range_max:  # 10 claims are in range
        submission_datetime_min = selected_claims.order_by("-submission_datetime")[range_min - 1].submission_datetime
        submission_datetime_max = selected_claims.order_by("-submission_datetime")[range_max - 1].submission_datetime
        claim_list = selected_claims.filter(submission_datetime__gte=submission_datetime_max).filter(
            submission_datetime__lte=submission_datetime_min).order_by("-submission_datetime")
    else:  # 1 to 9 claims are in range
        submission_datetime_min = selected_claims.order_by("-submission_datetime")[range_min - 1].submission_datetime
        claim_list = selected_claims.filter(submission_datetime__lte=submission_datetime_min).order_by(
            "-submission_datetime")

    # Get data for pagination
    max_pages = math.ceil(total_count / items_shown_per_page)
    clickable_pages = []
    newest_page = False
    oldest_page = False
    previous_page = False
    next_page = False
    for page in range(1, max_pages + 1):
        if (page_num - 2) <= page <= (page_num + 2):
            clickable_pages.append(page)
            if page == page_num - 1:
                previous_page = page
            elif page == page_num + 1:
                next_page = page
        else:
            if page == 1:
                newest_page = page
            if page == max_pages:
                oldest_page = page
    if clickable_pages == [1]:
        clickable_pages = None

    # Get URL info for back_view
    request.user.back_url = ",".join(["expensesapp:manager", group_url, str(page_num)])
    request.user.save()

    claim_groups = [{"name": "Your Team", "url_name": "your-team", "count": your_teams_claims_len},
                    {"name": "Other Teams", "url_name": "other-teams", "count": other_teams_claims_len}]
    return render(request, "expensesapp/manager.html", {"claim_list": claim_list,
                                                        "claim_groups": claim_groups,
                                                        "group_url": group_url,
                                                        "group_name": group_name,
                                                        "current_page": page_num,
                                                        "clickable_pages": clickable_pages,
                                                        "newest_page": newest_page,
                                                        "oldest_page": oldest_page,
                                                        "previous_page": previous_page,
                                                        "next_page": next_page})


@login_required
def claim_return_view(request, claim_ref):

    # Check that the claim exists
    try:
        claim = Claim.objects.get(reference=claim_ref)
    except Claim.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that the claim is one of the manager-user's pending claims (from their team or another team)
    if claim not in request.user.get_all_teams_pending_claims():
        return render(request, "expensesapp/access_denied.html")

    # Check that claim status is "Pending"
    if not claim.status == "2":
        return render(request, "expensesapp/access_denied.html")

    if request.method == "POST":
        claim_return_form = ClaimReturnForm(request.POST)
        if claim_return_form.is_valid():
            feedback_comment = claim_return_form.cleaned_data["feedback"]
            claim.return_to_claimant(request.user, feedback_comment)
            claim.save()
            return HttpResponseRedirect(reverse("expensesapp:manager", args=["your-team", 1]))
    return render(request, "expensesapp/access_denied.html")


@login_required
def claim_approve_view(request, claim_ref):

    # Check that the claim exists
    try:
        claim = Claim.objects.get(reference=claim_ref)
    except Claim.DoesNotExist:
        return render(request, "expensesapp/access_denied.html")

    # Check that the claim is one of the manager-user's pending claims
    if claim not in request.user.get_all_teams_pending_claims():
        return render(request, "expensesapp/access_denied.html")

    # Check that claim status is "Pending"
    if not claim.status == "2":
        return render(request, "expensesapp/access_denied.html")

    if request.method == "POST":
        claim_approve_form = ClaimApproveForm(request.POST, claim_ref=claim_ref)
        if claim_approve_form.is_valid():
            claim.approve(request.user)
            claim.save()
            return HttpResponseRedirect(reverse("expensesapp:manager", args=["your-team", 1]))
    return render(request, "expensesapp/access_denied.html")


@login_required
def back_view(request):
    url_components = request.user.back_url.split(",")
    return HttpResponseRedirect(reverse(url_components[0], args=[url_components[1], url_components[2]]))
