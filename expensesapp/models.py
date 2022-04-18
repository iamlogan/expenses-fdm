from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.dateformat import DateFormat
from django.utils.translation import gettext_lazy as _

from .custom import *


class Currency(models.Model):
    name = models.CharField(max_length=20, unique=True)
    iso_code = models.CharField(max_length=3)
    symbol = models.CharField(max_length=1)
    VAT_NAMES = [("1", "VAT"), ("2", "Sales Tax")]
    vat_name = models.CharField(max_length=1, choices=VAT_NAMES)

    class Meta:
        verbose_name_plural = "currencies"

    def __str__(self):
        return "{} ({})".format(self.name, self.iso_code)


class User(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    default_currency = models.ForeignKey("Currency", on_delete=models.CASCADE, default=None, blank=True, null=True)
    primary_manager = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="team_members",
                                        on_delete=models.SET_NULL, default=None, blank=True, null=True)
    substitute = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="other_managers",
                                   on_delete=models.SET_NULL, default=None, blank=True, null=True)
    username = models.CharField(max_length=150,unique=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
    back_url = models.CharField(max_length=60, default=None, blank=True, null=True)

    def __str__(self):
        return "{0} {1} ({2})".format(self.first_name, self.last_name, self.email)

    def count_claims_by_status(self, status):
        return len(self.claims.filter(status=status))

    def is_manager(self):
        if self.team_members.all() or self.other_managers.all():
            return True
        else:
            return False

    def is_direct_manager(self):
        if self.team_members.all():
            return True
        else:
            return False

    def get_your_teams_pending_claims(self):
        your_teams_claims = None
        for member in self.team_members.all():
            if not your_teams_claims:
                your_teams_claims = member.claims.filter(status="2")
            else:
                your_teams_claims.union(member.claims.filter(status="2"))
        return your_teams_claims

    def get_other_teams_pending_claims(self):
        other_teams_claims = None
        for manager in self.other_managers.all():
            for member in manager.team_members.all():
                if not other_teams_claims:
                    other_teams_claims = member.claims.filter(status="2")
                else:
                    other_teams_claims.union(member.claims.filter(status="2"))
        return other_teams_claims

    def get_all_teams_pending_claims(self):
        your_teams_claims = self.get_your_teams_pending_claims()
        other_teams_claims = self.get_other_teams_pending_claims()
        if your_teams_claims and other_teams_claims:
            return your_teams_claims.union(other_teams_claims)
        elif your_teams_claims:
            return your_teams_claims
        elif other_teams_claims:
            return other_teams_claims
        else:
            return None


class Claim(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="claims", on_delete=models.CASCADE)
    currency = models.ForeignKey("Currency", on_delete=models.CASCADE)
    reference = models.CharField(max_length=8)
    creation_datetime = models.DateTimeField()
    submission_datetime = models.DateTimeField(default=None, blank=True, null=True)
    approval_datetime = models.DateTimeField(default=None, blank=True, null=True)
    approval_manager = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="claims_approved",
                                         on_delete=models.SET_NULL, default=None, blank=True, null=True)
    status_update_datetime = models.DateTimeField()
    description = models.CharField(max_length=50)
    STATUSES = [("1", "Draft"), ("2", "Pending"), ("3", "Sent"), ("4", "Accepted"), ("5", "Rejected")]
    status = models.CharField(max_length=1, choices=STATUSES)

    @classmethod
    def create(cls, owner, currency, description):
        now = timezone.now()
        reference = get_unique_reference(cls, "C")
        status = "1"
        claim = cls(owner=owner, currency=currency, reference=reference, description=description, creation_datetime=now,
                    status=status, status_update_datetime=now)
        return claim

    def submit(self):
        self.status = 2
        now = timezone.now()
        self.submission_datetime = now
        self.status_update_datetime = now

    def return_to_claimant(self, author, feedback_comment):
        self.status = 5
        now = timezone.now()
        self.status_update_datetime = now
        action_desc = "After submission, this claim was rejected and returned to the claimant"
        new_feedback = Feedback.create(now, self, author, feedback_comment, action_desc)
        new_feedback.save()

    def approve(self, manager):
        self.status = 3
        now = timezone.now()
        self.status_update_datetime = now
        self.approval_datetime = now
        self.approval_manager = manager

    def is_editable(self):
        if (self.status == "1") or (self.status == "5"):
            return True
        else:
            return False

    def user_can_view(self, user):
        if self.owner == user:
            return True
        claims_user_can_view = user.get_all_teams_pending_claims()
        if claims_user_can_view:
            if self in claims_user_can_view:
                return True
        return False

    def get_receipts_list_sorted(self):
        return self.receipts.all().order_by("creation_datetime")

    def get_receipts_count(self):
        return len(self.receipts.all())

    def get_total_amount(self):
        total = 0
        for receipt in self.receipts.all():
            total += receipt.amount
        return total

    def get_total_vat(self):
        total = 0
        for receipt in self.receipts.all():
            total += receipt.vat
        return total

    def get_earliest_receipt(self):
        return self.receipts.all().earliest("date_incurred")

    def get_latest_receipt(self):
        return self.receipts.all().latest("date_incurred")

    def get_highest_vat(self):
        receipts = self.receipts.all()
        if len(receipts) == 0:
            return None
        elif len(receipts) == 1:
            receipt = receipts[0]
            return receipt.vat / receipt.amount * 100
        else:
            highest_vat_percent = 0
            for receipt in receipts:

                try:
                    receipt_vat = receipt.vat / receipt.amount * 100
                except ZeroDivisionError:
                    receipt_vat = 0

                if receipt_vat > highest_vat_percent:
                    highest_vat_percent = receipt_vat
            return highest_vat_percent

    def get_latest_feedback(self):
        return self.feedbacks.latest("creation_datetime")

    # Methods that return strings for display:

    def __str__(self):
        return "expenses claim {0}".format(self.reference)

    def get_string_creation_datetime(self):
        return self.creation_datetime

    def get_string_total_amount(self):
        return "{0} {1:0.2f}".format(self.currency.symbol, self.get_total_amount())

    def get_string_total_vat(self):
        return "{0} {1:0.2f}".format(self.currency.symbol, self.get_total_vat())

    def get_string_total_vat_and_percent(self):
        total_vat = self.get_total_vat()
        try:
            percentage = int(round(100 * total_vat / self.get_total_amount()))
            return "{0} {1:0.2f} ({2:d}%)".format(self.currency.symbol, total_vat, percentage)
        except ZeroDivisionError:
            return "{0} {1:0.2f}".format(self.currency.symbol, total_vat)

    def get_string_highest_vat(self):
        return "{0:d}%".format(int(self.get_highest_vat()))

    def get_string_dates_incurred(self):
        try:
            earliest_date = self.get_earliest_receipt().date_incurred
        except AttributeError:
            return None
        latest_date = self.get_latest_receipt().date_incurred
        formatted_earliest_date = DateFormat(earliest_date)
        formatted_latest_date = DateFormat(latest_date)
        if earliest_date == latest_date:
            return "{0}".format(formatted_earliest_date.format("jS M, Y"))
        else:
            if earliest_date.year == latest_date.year:
                if earliest_date.month == latest_date.month:
                    return "{0} – {1}".format(formatted_earliest_date.format("jS"),
                                              formatted_latest_date.format("jS M, Y"))
                else:
                    return "{0} – {1}".format(formatted_earliest_date.format("jS M"),
                                              formatted_latest_date.format("jS M, Y"))
            else:
                return "{0} – {1}".format(formatted_earliest_date.format("jS M, Y"),
                                          formatted_latest_date.format("jS M, Y"))


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Receipt(models.Model):
    claim = models.ForeignKey("Claim", related_name="receipts", on_delete=models.CASCADE)
    reference = models.CharField(max_length=10)
    creation_datetime = models.DateTimeField()
    date_incurred = models.DateField()
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    amount = models.FloatField()
    vat = models.FloatField()
    description = models.TextField(max_length=200)
    file = models.ImageField(default=None, blank=True, null=True)

    @classmethod
    def create(cls, claim, category, date_incurred, amount, vat, description):
        now = timezone.now()
        reference = get_unique_reference(cls, "R")
        receipt = cls(reference=reference, creation_datetime=now, claim=claim, category=category,
                      date_incurred=date_incurred, amount=amount, vat=vat, description=description)
        return receipt

    # Methods that return strings for display:

    def __str__(self):
        return "expense receipt {0}".format(self.reference)

    def get_string_amount(self):
        return "{0} {1:0.2f}".format(self.claim.currency.symbol, self.amount)

    def get_string_vat(self):
        return "{0} {1:0.2f}".format(self.claim.currency.symbol, self.vat)

    def get_string_vat_percent(self):
        return "{0:d}%".format(int(round(100 * self.vat / self.amount)))


class Feedback(models.Model):
    claim = models.ForeignKey("Claim", related_name="feedbacks", on_delete=models.CASCADE)
    creation_datetime = models.DateTimeField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="feedbacks", on_delete=models.CASCADE)
    comment = models.CharField(max_length=300)
    action_desc = models.CharField(max_length=100)

    @classmethod
    def create(cls, creation_datetime, claim, author, comment, action_desc):
        feedback = cls(claim=claim, creation_datetime=creation_datetime, author=author, comment=comment,
                       action_desc=action_desc)
        return feedback
