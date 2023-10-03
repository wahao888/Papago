from django import forms
# from django.core.exceptions import ValidationError
# from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    account = forms.CharField(max_length=100)
    pwd = forms.CharField(widget=forms.PasswordInput())

    # def clean_account(self):
    #     account = self.cleaned_data.get("account")
    #     dbuser = User.objects.filter(username=account)

    #     if not dbuser:
    #         return f"{account}-此帳號不存在"
    #     return account


