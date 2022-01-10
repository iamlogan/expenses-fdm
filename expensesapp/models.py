from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    # Overwriting to make fields required
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email address'))


class Claim(models.Model):
    creation_datetime = models.DateTimeField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=200, null=True)

    @classmethod
    def create(cls, owner, description):
        now = timezone.now()
        claim = cls(owner=owner, description=description, creation_datetime=now)
        return claim


class Receipt(models.Model):
    CATEGORIES = [
        ("ML", "Meal"),
        ("TI", "Taxi"),
    ]
    claim = models.ForeignKey("Claim", on_delete=models.SET_NULL, null=True)
    amount = models.FloatField()
    vat = models.FloatField()
    description = models.TextField(max_length=200)
    category = models.CharField(max_length=2, choices=CATEGORIES)
    date_incurred = models.DateField()
