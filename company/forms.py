from django import forms
from .models import Company, ContactPerson

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["ico", "name", "address", "city", "postal_code"]

class ContactPersonForm(forms.ModelForm):
    class Meta:
        model = ContactPerson
        fields = ["name", "email", "phone"]
