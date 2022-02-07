from .custom import get_unique_reference
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)


class Claim(models.Model):
    creation_datetime = models.DateTimeField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    description = models.CharField(max_length=50)
    reference = models.CharField(max_length=8, default="0")
    STATUSES = [
        ("1", "Draft"),
        ("2", "Pending"),
        ("3", "Sent")
    ]
    status = models.CharField(max_length=1, choices=STATUSES, default="1")

    @classmethod
    def create(cls, owner, description):
        now = timezone.now()
        reference = get_unique_reference(cls, "C")
        claim = cls(owner=owner, description=description, creation_datetime=now, reference=reference)
        return claim

    def user_can_access(self, user):
        return self.owner == user


class Receipt(models.Model):
    claim = models.ForeignKey("Claim", on_delete=models.CASCADE)
    amount = models.FloatField()
    vat = models.FloatField()
    description = models.TextField(max_length=200)
    CATEGORIES = [
        ("ML", "Meal"),
        ("TI", "Taxi"),
    ]
    category = models.CharField(max_length=2, choices=CATEGORIES)
    date_incurred = models.DateField()
