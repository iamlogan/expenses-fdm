from django import forms


class NewClaimForm(forms.Form):
    description = forms.CharField(label="Description", max_length=200, required=False)