from django import forms


class ClaimNewForm(forms.Form):
    description = forms.CharField(label="Description", max_length=50, required=False)


class ClaimEditForm(forms.Form):
    description = forms.CharField(label="Description", max_length=50, required=False)