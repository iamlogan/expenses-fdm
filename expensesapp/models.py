from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
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
    primary_manager = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="team_members", on_delete=models.CASCADE, default=None,
                                        blank=True, null=True)
    username = models.CharField(max_length=150,unique=False,)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return "{0} {1} ({2})".format(self.first_name, self.last_name, self.email)

    def is_manager(self):
        if self.get_team_members():
            return True
        else:
            return False

    def get_team_members(self):
        return self.team_members.all()

    def get_range_of_claims(self, start, end):
            try:
                creation_datetime_start = self.claims.order_by("-creation_datetime")[start].creation_datetime
            except IndexError:
                return None
            try:
                creation_datetime_end = self.claims.order_by("-creation_datetime")[end].creation_datetime
                return self.claims.filter(creation_datetime__lte=creation_datetime_start).filter(
                    creation_datetime__gt=creation_datetime_end).order_by("-creation_datetime")
            except IndexError:
                return self.claims.all()

    def count_claims_by_status(self, status):
        return len(self.claims.filter(status=status))


class Claim(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="claims", on_delete=models.CASCADE)
    currency = models.ForeignKey("Currency", on_delete=models.CASCADE)
    reference = models.CharField(max_length=8)
    creation_datetime = models.DateTimeField()
    submission_datetime = models.DateTimeField(default=None, blank=True, null=True)
    description = models.CharField(max_length=50)
    STATUSES = [("1", "Draft"), ("2", "Pending"), ("3", "Sent"), ("4", "Accepted"), ("5", "Rejected")]
    status = models.CharField(max_length=1, choices=STATUSES)

    @classmethod
    def create(cls, owner, currency, description):
        now = timezone.now()
        reference = get_unique_reference(cls, "C")
        status = "1"
        claim = cls(owner=owner, currency=currency, reference=reference, description=description, creation_datetime=now,
                    status=status)
        return claim

    def submit(self):
        self.status = 2
        self.submission_datetime = timezone.now()

    def user_can_view(self, user):
        if self.owner == user:
            return True
        elif self.owner in user.team_members.all():
            return True
        else:
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
            percentage = int(100 * total_vat / self.get_total_amount())
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

    @classmethod
    def create(cls, claim, category, date_incurred, amount, vat, description):
        now = timezone.now()
        reference = get_unique_reference(cls, "R")
        receipt = cls(reference=reference, creation_datetime=now, claim=claim, category=category,
                      date_incurred=date_incurred, amount=amount, vat=vat, description=description)
        return receipt

    def user_can_view(self, user):
        if self.claim.owner == user:
            return True
        elif self.claim.owner in user.team_members.all():
            return True
        else:
            return False

    # Methods that return strings for display:

    def __str__(self):
        return "expense receipt {0}".format(self.reference)

    def get_string_amount(self):
        return "{0} {1:0.2f}".format(self.claim.currency.symbol, self.amount)

    def get_string_vat(self):
        return "{0} {1:0.2f}".format(self.claim.currency.symbol, self.vat)

    def get_string_vat_percent(self):
        return "{0:d}%".format(int(100 * self.vat / self.amount))
