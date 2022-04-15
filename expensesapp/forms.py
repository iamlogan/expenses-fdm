import decimal
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone as django_timezone


class AccountEditForm(forms.Form):
    new_default = forms.ChoiceField(choices=[None])

    def __init__(self, *args, **kwargs):
        all_currencies = kwargs.pop("all_currencies")
        current_default = kwargs.pop("current_default")
        super().__init__(*args, **kwargs)
        choices = []
        for currency in all_currencies:
            if currency == current_default:
                choices.insert(0, (currency.name, str(currency)))
            else:
                choices.append((currency.name, str(currency)))
        self.fields["new_default"].choices = choices


class ClaimNewForm(forms.Form):
    currency = forms.ChoiceField(choices=[None])
    description = forms.CharField(max_length=50, required=False)

    def __init__(self, *args, **kwargs):
        all_currencies = kwargs.pop("all_currencies")
        default_currency = kwargs.pop("default_currency")
        super().__init__(*args, **kwargs)
        choices = []
        for currency in all_currencies:
            if currency == default_currency:
                choices.insert(0, (currency.name, str(currency)))
            else:
                choices.append((currency.name, str(currency)))
        self.fields["currency"].choices = choices

    def clean_description(self):
        data = self.cleaned_data["description"]
        if not data:
            raise ValidationError("Enter a description.")
        return data


class ClaimEditForm(forms.Form):
    description = forms.CharField(max_length=50, required=False)

    def __init__(self, *args, **kwargs):
        description = kwargs.pop("description")
        super().__init__(*args, **kwargs)
        self.fields["description"].initial = description

    def clean_description(self):
        data = self.cleaned_data["description"]
        if not data:
            raise ValidationError("Enter a description.")
        return data


class ClaimDeleteForm(forms.Form):
    claim = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        reference = kwargs.pop("claim_ref")
        super().__init__(*args, **kwargs)
        self.fields["claim"].initial = reference


class ReceiptNewForm(forms.Form):
    claim = forms.CharField(widget=forms.HiddenInput)
    date_incurred = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d'), initial=django_timezone.now())
    category = forms.ChoiceField(choices=[None])
    amount = forms.FloatField()
    vat = forms.FloatField()
    description = forms.CharField(max_length=50, required=False)

    def __init__(self, *args, **kwargs):
        claim_ref = kwargs.pop("claim_ref")
        categories = kwargs.pop("categories")
        super().__init__(*args, **kwargs)
        self.fields["claim"].initial = claim_ref
        self.fields["category"].choices = queryset_to_choices(categories)

    def clean(self):
        cleaned_data = super().clean()

        # Check that VAT is less than amount
        amount = cleaned_data.get("amount")
        vat = cleaned_data.get("vat")
        if vat and amount:
            if vat >= amount:
                raise ValidationError("Enter a value less than Amount.")

        return cleaned_data

    def clean_amount(self):
        data = self.cleaned_data["amount"]

        # Check that the amount is greater than 0.
        if data <= 0:
            raise ValidationError("Enter an amount greater than zero.")

        # Check that the amount has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("Enter a valid amount.")

        return data

    def clean_vat(self):
        data = self.cleaned_data["vat"]

        # Check that the vat is greater than or equal to 0.
        if data < 0:
            raise ValidationError("Enter a VAT greater or equal to zero.")

        # Check that the vat has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("Enter a valid VAT.")

        return data

    def clean_description(self):
        data = self.cleaned_data["description"]

        # Check that there is a description
        if not data:
            raise ValidationError("Enter a description.")

        return data


class ReceiptEditForm(forms.Form):
    date_incurred = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d'), initial=django_timezone.now())
    category = forms.ChoiceField(choices=[None])
    amount = forms.FloatField()
    vat = forms.FloatField()
    description = forms.CharField(max_length=50, required=False)

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop("categories")
        date_incurred = kwargs.pop("date_incurred")
        category = kwargs.pop("category")
        amount = kwargs.pop("amount")
        vat = kwargs.pop("vat")
        description = kwargs.pop("description")
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = queryset_to_choices(categories)
        self.fields["date_incurred"].initial = date_incurred
        self.fields["category"].initial = category
        self.fields["amount"].initial = "{0:0.2f}".format(amount)
        self.fields["vat"].initial = "{0:0.2f}".format(vat)
        self.fields["description"].initial = description

    def clean(self):
        cleaned_data = super().clean()

        # Check that VAT is less than amount
        amount = cleaned_data.get("amount")
        vat = cleaned_data.get("vat")
        if vat and amount:
            if vat >= amount:
                raise ValidationError("Enter a value less than Amount.")

        return cleaned_data

    def clean_amount(self):
        data = self.cleaned_data["amount"]

        # Check that the amount is greater than 0.
        if data <= 0:
            raise ValidationError("Enter an amount greater than zero.")

        # Check that the amount has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("Enter a valid amount.")

        return data

    def clean_vat(self):
        data = self.cleaned_data["vat"]

        # Check that the vat is greater than or equal to 0.
        if data < 0:
            raise ValidationError("Enter a VAT greater or equal to zero.")

        # Check that the vat has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("Enter a valid VAT.")

        return data

    def clean_description(self):
        data = self.cleaned_data["description"]

        # Check that there is a description
        if not data:
            raise ValidationError("Enter a description.")

        return data


class ReceiptDeleteForm(forms.Form):
    receipt = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        reference = kwargs.pop("receipt_ref")
        super().__init__(*args, **kwargs)
        self.fields["receipt"].initial = reference


class ClaimSubmitForm(forms.Form):
    claim = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        reference = kwargs.pop("claim_ref")
        super().__init__(*args, **kwargs)
        self.fields["claim"].initial = reference


# From a queryset, build a list of tuples, suitable for a form field's 'choices' attribute.
# Note: The entities must have a 'name' field. Assumes data to send is the same as visible choices.
def queryset_to_choices(queryset):
    output_list = []
    for entity in queryset:
        entity_string = entity.name
        entity_tuple = (entity_string, entity_string)
        output_list.append(entity_tuple)
    return output_list