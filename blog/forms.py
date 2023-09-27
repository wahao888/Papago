from django import forms
from django.core.exceptions import ValidationError
from blog.models import TravelLog
# from django.utils.translation import ugettext_lazy as _


class ProfileForm(forms.Form):
    name = forms.CharField(max_length=100)
    picture = forms.ImageField()


class TravelLogForm(forms.ModelForm):
    class Meta:
        model = TravelLog
        fields = ['title', 'content']
