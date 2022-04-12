from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone
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
    email = models.EmailField(_('email address'))
    default_currency = models.ForeignKey("Currency", on_delete=models.CASCADE)


class Claim(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    currency = models.ForeignKey("Currency", on_delete=models.CASCADE)
    reference = models.CharField(max_length=8)
    creation_datetime = models.DateTimeField()
    description = models.CharField(max_length=50)
    STATUSES = [("1", "Draft"), ("2", "Pending"), ("3", "Sent")]
    status = models.CharField(max_length=1, choices=STATUSES)

    @classmethod
    def create(cls, owner, currency, description):
        now = timezone.now()
        reference = get_unique_reference(cls, "C")
        status = "1"
        claim = cls(owner=owner, currency=currency, reference=reference, description=description, creation_datetime=now,
                    status=status)
        return claim

    def user_can_access(self, user):
        return self.owner == user

    def get_receipts_list(self):
        return Receipt.objects.filter(claim=self).order_by("creation_datetime")

    def get_receipts_count(self):
        return len(self.get_receipts_list())

    def get_total_amount(self):
        total = 0
        for receipt in self.get_receipts_list():
            total += receipt.amount
        return total

    def get_total_vat(self):
        total = 0
        for receipt in self.get_receipts_list():
            total += receipt.vat
        return total

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


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Receipt(models.Model):
    claim = models.ForeignKey("Claim", on_delete=models.CASCADE)
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

    def user_can_access(self, user):
        return self.claim.owner == user

    # Methods that return strings for display:

    def __str__(self):
        return "expense receipt {0}".format(self.reference)

    def get_string_amount(self):
        return "{0} {1:0.2f}".format(self.claim.currency.symbol, self.amount)

    def get_string_vat(self):
        return "{0} {1:0.2f}".format(self.claim.currency.symbol, self.vat)

    def get_string_vat_percent(self):
        return "{0:d}%".format(int(100 * self.vat / self.amount))
